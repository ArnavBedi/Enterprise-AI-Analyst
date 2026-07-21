import pandas as pd


class PythonExecutor:

    @staticmethod
    def execute(df: pd.DataFrame, code: str):
        """
        Executes AI-generated pandas code safely.
        """

        local_vars = {
            "df": df,
            "pd": pd
        }

        try:
            result = eval(
                code,
                {"__builtins__": {}},
                local_vars
            )

            return result

        except Exception as e:
            return f"Execution Error: {e}"