from typing import TypedDict, Optional, Any


class GraphState(TypedDict):

    # User request
    question: str

    # Data sources
    df: Optional[Any]
    report: Optional[dict]
    database_path: Optional[str]
    database_url: Optional[str]
    database_dialect: Optional[str]

    # Execution plan
    plan: list[str]
    current_step: int

    # Python Agent outputs
    python_code: Optional[str]
    python_result: Optional[Any]

    # Chart Agent outputs
    chart_code: Optional[str]
    figure: Optional[Any]

    # SQL Agent outputs
    sql: Optional[str]
    sql_result: Optional[Any]

    # Final synthesized response
    answer: Optional[str]

    # Error information
    error: Optional[str]
