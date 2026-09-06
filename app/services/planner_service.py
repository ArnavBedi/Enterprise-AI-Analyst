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

    def create_plan(self, question: str) -> list[str]:

        prompt = f"""
You are the planning component of an enterprise AI data analyst.

Determine which agents are required to fulfill the user's request.

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

5. Use business last when the user requests interpretation,
   explanation, recommendations, or a summary of previous analysis.

6. Do not invent additional agents.

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

        return list(plan)
