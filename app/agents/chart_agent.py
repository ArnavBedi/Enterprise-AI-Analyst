from app.services.chart_service import ChartService
from app.tools.python_executor import PythonExecutor
from app.state.graph_state import GraphState
import pandas as pd


class ChartAgent:

    def __init__(self):
        self.chart = ChartService()

    def run(self, state: GraphState):

        source = next(
            (
                value
                for value in (
                    state.get("sql_result"),
                    state.get("prior_sql_result"),
                    state.get("python_result"),
                    state.get("prior_python_result"),
                    state.get("df"),
                )
                if isinstance(value, (pd.DataFrame, pd.Series))
            ),
            None,
        )
        if source is None:
            state["error"] = "Charting was requested, but no tabular data is available."
            return state
        if isinstance(source, pd.Series):
            source = source.reset_index()

        code = self.chart.generate_chart(
            source,
            state["question"],
            conversation_history=state.get("conversation_history", []),
        )

        figure = PythonExecutor.execute_chart(
            source,
            code
        )

        state["chart_code"] = code
        state["figure"] = figure
        state["chart_source"] = (
            "SQL result"
            if source is state.get("sql_result") or source is state.get("prior_sql_result")
            else "CSV/Python result"
        )

        return state
