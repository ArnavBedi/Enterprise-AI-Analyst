from typing import Literal
from pydantic import BaseModel

from app.services.gemini_client import GeminiClient


AgentName = Literal[
    "python",
    "chart",
    "sql",
    "business"
]


class AgentPlan(BaseModel):
    plan: list[AgentName]


class PlannerService:

    def __init__(self):
        self.gemini = GeminiClient()

    def create_plan(
        self,
        question: str,
        conversation_history=None,
        has_csv: bool = False,
        has_database: bool = False,
        has_prior_sql_result: bool = False,
    ) -> list[str]:

        recent_history = (conversation_history or [])[-6:]

        prompt = f"""
You are the planning component of an enterprise AI data analyst.

Determine which agents are required to fulfill the user's request.

Available context:
- CSV available: {has_csv}
- Database connected: {has_database}
- Prior SQL result available: {has_prior_sql_result}
- Recent conversation: {recent_history}

Available agents:

python
- calculations
- statistics
- aggregations
- filtering
- numerical data analysis

chart
- plots
- graphs
- charts
- visualizations

sql
- SQLite, PostgreSQL, and other connected relational databases
- SQL queries
- database analysis

business
- summaries
- explanations
- business insights
- recommendations
- interpretation

Rules:

1. Only choose from:
   python, chart, sql, business

2. Include only agents that are actually needed.

3. Agents must appear in execution order.

4. Use python before chart when calculations are required first.

5. For a connected database request that also asks for a chart, use sql then
   chart. If a prior SQL result is available and the user says "visualize that"
   or similar, use chart without rerunning SQL unless new data is requested.

6. Use business last when the user requests interpretation,
   explanation, recommendations, or a summary of previous analysis.

7. Resolve pronouns such as "that", "it", and "those results" from the recent
   conversation.

8. Do not use python when no CSV or prior tabular result is available.

9. Do not invent additional agents.

Examples:

"Calculate the average salary"
-> python

"Plot salary versus age"
-> chart

"Calculate average salary and plot salary versus age"
-> python, chart

"Calculate average salary, plot it, and explain the findings"
-> python, chart, business

"Use SQL to calculate average salary by department"
-> sql

"Use the database to calculate average salary and chart it"
-> sql, chart

After a SQL result, "Now visualize that and explain it"
-> chart, business

User request:

{question}
"""

        result = self.gemini.generate_json(
            prompt,
            AgentPlan
        )

        if isinstance(result, AgentPlan):
            plan = result.plan
        else:
            plan = AgentPlan.model_validate(result).plan

        if not plan:
            return ["business"]
        plan = list(plan)
        if "chart" in plan and has_database and not has_prior_sql_result:
            if "sql" not in plan and not has_csv:
                plan.insert(plan.index("chart"), "sql")
        if "python" in plan and not has_csv and has_database:
            plan = ["sql" if agent == "python" else agent for agent in plan]
        return list(dict.fromkeys(plan))
