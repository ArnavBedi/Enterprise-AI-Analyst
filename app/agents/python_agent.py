from app.services.python_service import PythonService
from app.state.graph_state import GraphState
import pandas as pd


class PythonAgent:

    def __init__(self):
        self.python = PythonService()

    def run(self, state: GraphState):

        source = state.get("df")
        if source is None:
            source = state.get("prior_sql_result")
        if not isinstance(source, pd.DataFrame):
            state["error"] = "Python analysis was requested, but no tabular data is available."
            return state

        code, result = self.python.ask(
            source,
            state["question"],
            conversation_history=state.get("conversation_history", []),
        )

        state["python_code"] = code
        state["python_result"] = result

        return state
