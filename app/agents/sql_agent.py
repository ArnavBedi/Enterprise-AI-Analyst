from app.services.sql_service import SQLService
from app.tools.sql_executor import SQLExecutor
from app.state.graph_state import GraphState
from app.database.connection import DatabaseConnection, DatabaseError
from app.security.audit import query_fingerprint, record_audit_event


class SQLAgent:

    def __init__(self):
        self.sql_service = SQLService()

    def run(self, state: GraphState):

        database_url = state.get("database_url")
        database_path = state.get("database_path")
        question = state.get("question")

        # -------------------------
        # Validate Database
        # -------------------------

        if not database_url and not database_path:

            state["error"] = (
                "SQL analysis was requested, but no database is connected."
            )

            state["answer"] = (
                "Upload a SQLite database or configure the PostgreSQL connection."
            )

            return state

        try:

            # -------------------------
            # Generate SQL
            # -------------------------

            database = (
                DatabaseConnection(
                    database_url,
                    profile_name=state.get("database_profile") or "Default",
                )
                if database_url
                else DatabaseConnection.from_sqlite_path(database_path)
            )
            state["database_dialect"] = database.dialect
            sql = self.sql_service.generate_sql(
                database,
                question,
                conversation_history=state.get("conversation_history", []),
            )

            state["sql"] = sql

            # -------------------------
            # Execute SQL
            # -------------------------

            result = SQLExecutor.execute(
                database,
                sql
            )

            state["sql_result"] = result
            state["sql_diagnostics"] = {
                key: result.attrs.get(key)
                for key in (
                    "profile",
                    "database",
                    "dialect",
                    "row_count",
                    "duration_ms",
                    "truncated",
                    "max_rows",
                    "estimated_cost",
                )
            }
            record_audit_event(
                "sql_query",
                success=True,
                profile=database.profile_name,
                dialect=database.dialect,
                query_id=query_fingerprint(sql),
                row_count=result.attrs.get("row_count"),
                duration_ms=result.attrs.get("duration_ms"),
                truncated=result.attrs.get("truncated"),
                estimated_cost=result.attrs.get("estimated_cost"),
            )

            return state

        except DatabaseError as e:

            record_audit_event(
                "sql_query",
                success=False,
                profile=state.get("database_profile"),
                dialect=state.get("database_dialect"),
                reason=str(e),
            )

            state["error"] = (
                f"SQL analysis failed: {e}"
            )

            return state
        except Exception:
            state["error"] = "SQL analysis failed unexpectedly."
            return state
