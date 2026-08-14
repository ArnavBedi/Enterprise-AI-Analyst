from app.services.analyst_service import AnalystService
from app.state.graph_state import GraphState


class BusinessAgent:

    def __init__(self):
        self.analyst = AnalystService()

    def run(self, state: GraphState):

        state["answer"] = self.analyst.analyze(
            state["report"]
        )

        return state