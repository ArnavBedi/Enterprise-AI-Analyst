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

        state["code"] = code
        state["answer"] = result

        return state