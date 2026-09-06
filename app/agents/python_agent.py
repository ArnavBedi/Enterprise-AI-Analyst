from app.services.python_service import PythonService
from app.state.graph_state import GraphState


class PythonAgent:

    def __init__(self):
        self.python = PythonService()

    def run(self, state: GraphState):

        code, result = self.python.ask(
            state["df"],
            state["question"]
        )

        state["python_code"] = code
        state["python_result"] = result

        return state