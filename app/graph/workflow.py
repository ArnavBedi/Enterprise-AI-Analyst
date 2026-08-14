from langgraph.graph import StateGraph, END

from app.state.graph_state import GraphState

from app.agents.business_agent import BusinessAgent
from app.agents.python_agent import PythonAgent
from app.agents.sql_agent import SQLAgent
from app.agents.chart_agent import ChartAgent


business = BusinessAgent()
python = PythonAgent()
sql = SQLAgent()
chart = ChartAgent()


# -------------------------
# Router
# -------------------------

def router(state: GraphState):

    question = state["question"].lower()

    plan = []

    chart_keywords = [
        "plot",
        "graph",
        "chart",
        "scatter",
        "histogram",
        "bar",
        "line",
        "boxplot"
    ]

    sql_keywords = [
        "sql",
        "database",
        "sqlite",
        "table"
    ]

    python_keywords = [
        "average",
        "sum",
        "count",
        "maximum",
        "minimum",
        "calculate",
        "correlation"
    ]

    business_keywords = [
        "summarize",
        "summary",
        "explain",
        "insight",
        "recommend",
        "analyze"
    ]

    # Determine required agents

    if any(word in question for word in sql_keywords):
        plan.append("sql")

    if any(word in question for word in python_keywords):
        plan.append("python")

    if any(word in question for word in chart_keywords):
        plan.append("chart")

    if any(word in question for word in business_keywords):
        plan.append("business")

    # Default to business analysis
    if not plan:
        plan.append("business")

    state["plan"] = plan
    state["current_step"] = 0

    return state


# -------------------------
# Agent Nodes
# -------------------------

def business_node(state: GraphState):
    return business.run(state)


def python_node(state: GraphState):
    return python.run(state)


def sql_node(state: GraphState):
    return sql.run(state)


def chart_node(state: GraphState):
    return chart.run(state)


# -------------------------
# Next Agent
# -------------------------

def route_next(state: GraphState):

    plan = state["plan"]
    current_step = state["current_step"]

    if current_step >= len(plan):
        return END

    return plan[current_step]


# -------------------------
# Advance Step
# -------------------------

def advance_step(state: GraphState):

    state["current_step"] += 1

    return state


# -------------------------
# Build Graph
# -------------------------

graph = StateGraph(GraphState)

graph.add_node("router", router)

graph.add_node("business", business_node)
graph.add_node("python", python_node)
graph.add_node("sql", sql_node)
graph.add_node("chart", chart_node)

graph.add_node("advance", advance_step)

graph.set_entry_point("router")


# Router → first agent

graph.add_conditional_edges(
    "router",
    route_next,
    {
        "business": "business",
        "python": "python",
        "sql": "sql",
        "chart": "chart",
        END: END
    }
)


# Agents → advance

graph.add_edge("business", "advance")
graph.add_edge("python", "advance")
graph.add_edge("sql", "advance")
graph.add_edge("chart", "advance")


# Advance → next agent

graph.add_conditional_edges(
    "advance",
    route_next,
    {
        "business": "business",
        "python": "python",
        "sql": "sql",
        "chart": "chart",
        END: END
    }
)


workflow = graph.compile()