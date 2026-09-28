from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import NullPool


class DatabaseError(RuntimeError):
    """A safe, user-facing database error."""


@dataclass(frozen=True)
class DatabaseConnection:
    """SQLAlchemy-backed, read-only connection to a supported database."""

    url: str
    max_rows: int = 1000
    profile_name: str = "Uploaded SQLite"

    @classmethod
    def from_sqlite_path(cls, database_path: str) -> "DatabaseConnection":
        path = Path(database_path).expanduser().resolve()
        return cls(f"sqlite:///{path}", profile_name="Uploaded SQLite")

    @classmethod
    def from_environment(
        cls,
        variable: str = "DATABASE_URL",
    ) -> "DatabaseConnection":
        url = os.getenv(variable, "").strip()
        if not url:
            raise DatabaseError(
                f"{variable} is not configured. Add it to your .env file."
            )
        return cls(url, profile_name=variable)

    @property
    def dialect(self) -> str:
        try:
            return make_url(self.url).get_backend_name()
        except Exception as exc:
            raise DatabaseError("The database URL is invalid.") from exc

    @property
    def safe_label(self) -> str:
        parsed = make_url(self.url)
        if self.dialect == "sqlite":
            return f"SQLite: {parsed.database}"
        host = parsed.host or "unknown host"
        database = parsed.database or "unknown database"
        dialect_label = {
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
        }.get(self.dialect, self.dialect.title())
        return f"{dialect_label}: {database} on {host}"

    @property
    def statement_timeout_ms(self) -> int:
        return _bounded_integer("QUERY_TIMEOUT_MS", 15000, minimum=1000, maximum=120000)

    @property
    def max_query_cost(self) -> float:
        try:
            return max(0.0, float(os.getenv("MAX_POSTGRES_QUERY_COST", "100000")))
        except ValueError:
            return 100000.0

    def _engine(self) -> Engine:
        if self.dialect not in {"sqlite", "postgresql", "mysql"}:
            raise DatabaseError(
                f"Unsupported database type: {self.dialect}. "
                "Supported types are SQLite, PostgreSQL, and MySQL."
            )

        self._validate_allowed_host()
        options: dict[str, Any] = {
            "pool_pre_ping": True,
            "poolclass": NullPool,
        }
        if self.dialect == "postgresql":
            options["connect_args"] = {
                "options": (
                    "-c default_transaction_read_only=on "
                    f"-c statement_timeout={self.statement_timeout_ms}"
                ),
                "connect_timeout": 5,
            }
        elif self.dialect == "mysql":
            options["connect_args"] = {
                "connect_timeout": 5,
                "read_timeout": max(1, self.statement_timeout_ms // 1000),
            }

        return create_engine(self.url, **options)

    def test(self) -> str:
        engine = self._engine()
        try:
            with engine.connect() as connection:
                self._set_read_only(connection)
                connection.execute(text("SELECT 1"))
            return self.safe_label
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Could not connect to the database. Check the host, port, "
                "database name, credentials, and read-only permissions."
            ) from exc
        finally:
            engine.dispose()

    def schema(self) -> str:
        engine = self._engine()
        try:
            inspector = inspect(engine)
            schema_names = self._schema_names(inspector)
            lines = [f"SQL dialect: {self.dialect}"]

            relationship_lines: list[str] = []
            object_count = 0
            max_objects = _bounded_integer("MAX_SCHEMA_OBJECTS", 100, 1, 500)
            max_columns = _bounded_integer("MAX_COLUMNS_PER_TABLE", 100, 1, 500)
            for schema_name in schema_names:
                table_names = inspector.get_table_names(schema=schema_name)
                view_names = inspector.get_view_names(schema=schema_name)
                for object_name in sorted(set(table_names + view_names)):
                    if object_count >= max_objects:
                        lines.append(f"\nSchema output limited to {max_objects} objects.")
                        break
                    object_count += 1
                    qualified = (
                        f"{schema_name}.{object_name}"
                        if schema_name
                        else object_name
                    )
                    kind = "view" if object_name in view_names else "table"
                    lines.append(f"\n{kind.title()}: {qualified}")
                    columns = inspector.get_columns(
                        object_name,
                        schema=schema_name,
                    )
                    for column in columns[:max_columns]:
                        nullable = "nullable" if column.get("nullable") else "required"
                        lines.append(
                            f"- {column['name']} ({column['type']}, {nullable})"
                        )
                    if kind == "view":
                        continue
                    primary_key = inspector.get_pk_constraint(
                        object_name, schema=schema_name
                    ).get("constrained_columns") or []
                    if primary_key:
                        lines.append(f"- Primary key: {', '.join(primary_key)}")
                    for foreign_key in inspector.get_foreign_keys(
                        object_name, schema=schema_name
                    ):
                        source = ", ".join(foreign_key.get("constrained_columns") or [])
                        target_table = foreign_key.get("referred_table")
                        target_schema = foreign_key.get("referred_schema")
                        target_columns = ", ".join(
                            foreign_key.get("referred_columns") or []
                        )
                        target = (
                            f"{target_schema}.{target_table}"
                            if target_schema
                            else str(target_table)
                        )
                        relationship_lines.append(
                            f"- {qualified}.{source} -> {target}.{target_columns}"
                        )

            if len(lines) == 1:
                lines.append("No accessible tables or views were found.")
            if relationship_lines:
                lines.append("\nRelationships:")
                lines.extend(relationship_lines)
            return "\n".join(lines)
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "Connected, but could not inspect the database schema."
            ) from exc
        finally:
            engine.dispose()

    def execute_read_only(self, query: str) -> pd.DataFrame:
        from app.database.sql_safety import validate_read_only_sql

        safe_query = validate_read_only_sql(query)
        engine = self._engine()
        started = time.perf_counter()
        try:
            with engine.connect() as connection:
                self._set_read_only(connection)
                estimated_cost = self._enforce_query_cost(connection, safe_query)
                result = connection.execute(text(safe_query))
                rows = result.fetchmany(self.max_rows + 1)
                truncated = len(rows) > self.max_rows
                frame = pd.DataFrame(rows[: self.max_rows], columns=result.keys())
                frame.attrs["truncated"] = truncated
                frame.attrs["max_rows"] = self.max_rows
                frame.attrs["row_count"] = len(frame)
                frame.attrs["duration_ms"] = round(
                    (time.perf_counter() - started) * 1000,
                    2,
                )
                frame.attrs["database"] = self.safe_label
                frame.attrs["profile"] = self.profile_name
                frame.attrs["dialect"] = self.dialect
                frame.attrs["estimated_cost"] = estimated_cost
                return frame
        except SQLAlchemyError as exc:
            raise DatabaseError(
                "The read-only query failed. Review the generated SQL and schema."
            ) from exc
        finally:
            engine.dispose()

    def _schema_names(self, inspector: Any) -> list[str | None]:
        if self.dialect == "sqlite":
            return [None]
        if self.dialect == "postgresql":
            excluded = {"information_schema", "pg_catalog", "pg_toast"}
            return [
                name
                for name in inspector.get_schema_names()
                if name not in excluded and not name.startswith("pg_")
            ]
        if self.dialect == "mysql":
            return [None]
        return [None]

    def _set_read_only(self, connection: Any) -> None:
        if self.dialect == "sqlite":
            connection.exec_driver_sql("PRAGMA query_only = ON")
        elif self.dialect == "mysql":
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")
            connection.exec_driver_sql(
                f"SET SESSION MAX_EXECUTION_TIME = {self.statement_timeout_ms}"
            )

    def _enforce_query_cost(self, connection: Any, query: str) -> float | None:
        if self.dialect != "postgresql" or self.max_query_cost <= 0:
            return None
        plan = connection.execute(text(f"EXPLAIN (FORMAT JSON) {query}")).scalar_one()
        if isinstance(plan, str):
            import json

            plan = json.loads(plan)
        estimated_cost = float(plan[0]["Plan"]["Total Cost"])
        if estimated_cost > self.max_query_cost:
            raise DatabaseError(
                "The query was blocked because its estimated database cost is too high."
            )
        return estimated_cost

    def _validate_allowed_host(self) -> None:
        if self.dialect == "sqlite":
            return
        configured = os.getenv("ALLOWED_DATABASE_HOSTS", "").strip()
        if not configured:
            return
        allowed = {host.strip().lower() for host in configured.split(",") if host.strip()}
        host = (make_url(self.url).host or "").lower()
        if host not in allowed:
            raise DatabaseError("This database host is not on the connection allowlist.")


def _bounded_integer(
    variable: str,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    try:
        value = int(os.getenv(variable, str(default)))
    except ValueError:
        value = default
    return min(max(value, minimum), maximum)
