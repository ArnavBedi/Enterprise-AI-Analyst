from app.services.chart_service import ChartService
from app.tools.python_executor import PythonExecutor
from app.state.graph_state import GraphState


class ChartAgent:

    def __init__(self):
        self.chart = ChartService()

    def run(self, state: GraphState):

        code = self.chart.generate_chart(
            state["df"],
            state["question"]
        )

        figure = PythonExecutor.execute_chart(
            state["df"],
            code
        )

        state["chart_code"] = code
        state["figure"] = figure

        return state