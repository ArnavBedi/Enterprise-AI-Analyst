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
    database_profile: Optional[str]

    # Conversation context
    conversation_history: list[dict[str, str]]
    prior_question: Optional[str]
    prior_answer: Optional[str]
    prior_python_result: Optional[Any]
    prior_sql_result: Optional[Any]

    # Execution plan
    plan: list[str]
    current_step: int

    # Python Agent outputs
    python_code: Optional[str]
    python_result: Optional[Any]

    # Chart Agent outputs
    chart_code: Optional[str]
    chart_source: Optional[str]
    figure: Optional[Any]

    # SQL Agent outputs
    sql: Optional[str]
    sql_result: Optional[Any]
    sql_diagnostics: Optional[dict]

    # Final synthesized response
    answer: Optional[str]

    # Error information
    error: Optional[str]
