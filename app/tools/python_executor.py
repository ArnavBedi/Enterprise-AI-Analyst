import pandas as pd
import plotly.express as px


class PythonExecutor:

    @staticmethod
    def execute(df: pd.DataFrame, code: str):
        """
        Executes AI-generated Python code safely.
        The generated code must assign its final output
        to a variable called 'result'.
        """

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