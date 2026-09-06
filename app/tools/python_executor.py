import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class PythonExecutor:

    SAFE_BUILTINS = {
        "dict": dict,
        "list": list,
        "tuple": tuple,
        "set": set,
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "len": len,
        "min": min,
        "max": max,
        "sum": sum,
        "round": round,
        "abs": abs,
        "range": range,
        "enumerate": enumerate,
        "zip": zip,
        "sorted": sorted,
    }

    @staticmethod
    def execute(df: pd.DataFrame, code: str):

        local_vars = {
            "df": df,
            "pd": pd,
            "px": px,
            "go": go
        }

        try:
            exec(
                code,
                {"__builtins__": PythonExecutor.SAFE_BUILTINS},
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
            "px": px,
            "go": go
        }

        try:
            exec(
                code,
                {"__builtins__": PythonExecutor.SAFE_BUILTINS},
                local_vars
            )

            figure = (
                local_vars.get("fig")
                or local_vars.get("result")
            )

            if figure is None:
                raise ValueError(
                    "Generated code did not produce a Plotly figure."
                )

            return figure

        except Exception as e:
            raise RuntimeError(
                f"Chart execution failed: {e}"
            ) from e