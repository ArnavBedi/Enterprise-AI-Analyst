from app.services.sql_service import SQLService
from app.state.graph_state import GraphState


class SQLAgent:

    def __init__(self):
        self.sql = SQLService()

    def run(self, state: GraphState):

        sql, result = self.sql.ask(
            state["database_path"],
            state["question"]
        )

        state["sql"] = sql
        state["sql_result"] = result

        return state