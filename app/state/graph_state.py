from typing import TypedDict, Optional, Any


class GraphState(TypedDict):

    # User request
    question: str

    # Uploaded CSV
    df: Optional[Any]

    # Dataset inspection report
    report: Optional[dict]

    # SQLite database path
    database_path: Optional[str]

    # Agent execution plan
    plan: list[str]

    # Current position in the plan
    current_step: int

    # Outputs
    answer: Optional[str]

    code: Optional[str]

    figure: Optional[Any]

    sql: Optional[str]

    sql_result: Optional[Any]

    # Error information
    error: Optional[str]