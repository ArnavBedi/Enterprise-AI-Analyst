from app.services.sql_service import SQLService
from app.tools.sql_executor import SQLExecutor
from app.state.graph_state import GraphState
from app.database.connection import DatabaseConnection, DatabaseError


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
                DatabaseConnection(database_url)
                if database_url
                else DatabaseConnection.from_sqlite_path(database_path)
            )
            state["database_dialect"] = database.dialect
            sql = self.sql_service.generate_sql(database, question)

            state["sql"] = sql

            # -------------------------
            # Execute SQL
            # -------------------------

            result = SQLExecutor.execute(
                database,
                sql
            )

            state["sql_result"] = result

            return state

        except DatabaseError as e:

            state["error"] = (
                f"SQL analysis failed: {e}"
            )

            return state
        except Exception:
            state["error"] = "SQL analysis failed unexpectedly."
            return state
