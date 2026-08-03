import pandas as pd
import plotly.express as px


class PythonExecutor:

    @staticmethod
    def execute(df: pd.DataFrame, code: str):
        local_vars = {
            "df": df,
            "pd": pd,
            "px": px
        }

        try:
            exec(
                code,
                {"__builtins__": {}},
                local_vars
            )

            return local_vars.get("result")

        except Exception as e:
            return f"Execution Error:\n\n{e}"

    @staticmethod
    def execute_chart(df: pd.DataFrame, code: str):
        local_vars = {
            "df": df,
            "pd": pd,
            "px": px
        }

        exec(
            code,
            {"__builtins__": {}},
            local_vars
        )

        figure = local_vars.get("fig") or local_vars.get("result")

        if figure is None:
            raise ValueError(
                "The generated code did not produce a Plotly figure. It must assign the chart to either 'fig' or 'result'."
            )

        return figure