from __future__ import annotations

import os
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

    @classmethod
    def from_sqlite_path(cls, database_path: str) -> "DatabaseConnection":
        path = Path(database_path).expanduser().resolve()
        return cls(f"sqlite:///{path}")

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
        return cls(url)

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
        return f"{self.dialect.title()}: {database} on {host}"

    def _engine(self) -> Engine:
        if self.dialect not in {"sqlite", "postgresql", "mysql"}:
            raise DatabaseError(
                f"Unsupported database type: {self.dialect}. "
                "Supported types are SQLite, PostgreSQL, and MySQL."
            )

        options: dict[str, Any] = {
            "pool_pre_ping": True,
            "poolclass": NullPool,
        }
        if self.dialect == "postgresql":
            options["connect_args"] = {
                "options": "-c default_transaction_read_only=on",
                "connect_timeout": 5,
            }
        elif self.dialect == "mysql":
            options["connect_args"] = {"connect_timeout": 5}

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

            for schema_name in schema_names:
                table_names = inspector.get_table_names(schema=schema_name)
                view_names = inspector.get_view_names(schema=schema_name)
                for object_name in sorted(set(table_names + view_names)):
                    qualified = (
                        f"{schema_name}.{object_name}"
                        if schema_name
                        else object_name
                    )
                    kind = "view" if object_name in view_names else "table"
                    lines.append(f"\n{kind.title()}: {qualified}")
                    for column in inspector.get_columns(
                        object_name,
                        schema=schema_name,
                    ):
                        nullable = "nullable" if column.get("nullable") else "required"
                        lines.append(
                            f"- {column['name']} ({column['type']}, {nullable})"
                        )

            if len(lines) == 1:
                lines.append("No accessible tables or views were found.")
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
        try:
            with engine.connect() as connection:
                self._set_read_only(connection)
                result = connection.execute(text(safe_query))
                rows = result.fetchmany(self.max_rows + 1)
                truncated = len(rows) > self.max_rows
                frame = pd.DataFrame(rows[: self.max_rows], columns=result.keys())
                frame.attrs["truncated"] = truncated
                frame.attrs["max_rows"] = self.max_rows
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
