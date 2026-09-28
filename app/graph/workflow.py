from langgraph.graph import StateGraph, END

from app.state.graph_state import GraphState

from app.agents.business_agent import BusinessAgent
from app.agents.python_agent import PythonAgent
from app.agents.sql_agent import SQLAgent
from app.agents.chart_agent import ChartAgent
from app.services.planner_service import PlannerService


business = BusinessAgent()
python = PythonAgent()
sql = SQLAgent()
chart = ChartAgent()
planner = PlannerService()

# -------------------------
# Router
# -------------------------

def router(state: GraphState):

    plan = planner.create_plan(
        state["question"],
        conversation_history=state.get("conversation_history", []),
        has_csv=state.get("df") is not None,
        has_database=bool(
            state.get("database_url") or state.get("database_path")
        ),
        has_prior_sql_result=state.get("prior_sql_result") is not None,
    )

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

    if state.get("error"):
        return END

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
