import pandas as pd

from app.graph.workflow import workflow
from app.tools.dataset_inspector import DatasetInspector


df = pd.read_csv("data/sample.csv")

report = DatasetInspector.inspect(df)


state = {
    "question": (
        "Calculate the average salary, "
        "plot salary vs age, and explain the result."
    ),

    "df": df,
    "report": report,
    "database_path": None,
    "database_url": None,
    "database_dialect": None,

    "plan": [],
    "current_step": 0,

    "python_code": None,
    "python_result": None,

    "chart_code": None,
    "figure": None,

    "sql": None,
    "sql_result": None,

    "answer": None,
    "error": None
}


result = workflow.invoke(state)


print("\nPLAN:")
print(result["plan"])

print("\nPYTHON CODE:")
print(result["python_code"])

print("\nPYTHON RESULT:")
print(result["python_result"])

print("\nCHART CODE:")
print(result["chart_code"])

print("\nFINAL ANSWER:")
print(result["answer"])

print("\nFIGURE:")
print(result["figure"])
