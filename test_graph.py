import pandas as pd

from app.graph.workflow import workflow


state = {
    "question": "Calculate the average salary and plot salary vs age.",
    "df": pd.read_csv("data/sample.csv"),
    "report": {},
    "database_path": None,

    "plan": [],
    "current_step": 0,

    "answer": None,
    "code": None,
    "figure": None,

    "sql": None,
    "sql_result": None,

    "error": None
}


result = workflow.invoke(state)

print("\nPLAN:")
print(result["plan"])

print("\nCURRENT STEP:")
print(result["current_step"])

print("\nANSWER:")
print(result["answer"])

print("\nCODE:")
print(result["code"])

print("\nFIGURE:")
print(result["figure"])