import ast

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class PythonExecutor:

    FORBIDDEN_NODES = (
        ast.Import,
        ast.ImportFrom,
        ast.FunctionDef,
        ast.AsyncFunctionDef,
        ast.ClassDef,
        ast.Lambda,
        ast.Global,
        ast.Nonlocal,
        ast.With,
        ast.AsyncWith,
        ast.Try,
        ast.Raise,
    )

    FORBIDDEN_CALLS = {
        "eval",
        "exec",
        "compile",
        "open",
        "input",
        "getattr",
        "setattr",
        "delattr",
        "globals",
        "locals",
        "vars",
        "dir",
        "help",
        "breakpoint",
        "__import__",
        "system",
        "popen",
        "spawn",
        "unlink",
        "remove",
        "rmdir",
        "mkdir",
        "makedirs",
        "rename",
        "replace",
        "to_csv",
        "to_excel",
        "to_pickle",
        "to_sql",
        "to_json",
        "to_parquet",
        "to_feather",
        "to_hdf",
        "read_csv",
        "read_excel",
        "read_sql",
        "read_pickle",
        "read_parquet",
        "read_json",
    }

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

        PythonExecutor._validate_code(code)

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

        PythonExecutor._validate_code(code)

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

    @staticmethod
    def _validate_code(code: str) -> None:
        try:
            tree = ast.parse(code, mode="exec")
        except SyntaxError as exc:
            raise ValueError("Generated Python code is not valid.") from exc

        for node in ast.walk(tree):
            if isinstance(node, PythonExecutor.FORBIDDEN_NODES):
                raise ValueError(
                    f"Generated Python contains prohibited syntax: "
                    f"{type(node).__name__}."
                )
            if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
                raise ValueError("Private Python attributes are not allowed.")
            if isinstance(node, ast.Name) and node.id.startswith("__"):
                raise ValueError("Private Python names are not allowed.")
            if isinstance(node, ast.Call):
                function_name = None
                if isinstance(node.func, ast.Name):
                    function_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    function_name = node.func.attr
                if function_name in PythonExecutor.FORBIDDEN_CALLS:
                    raise ValueError(
                        f"Generated Python attempted a prohibited operation: "
                        f"{function_name}."
                    )
