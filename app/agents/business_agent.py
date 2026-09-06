from app.services.gemini_client import GeminiClient
from app.state.graph_state import GraphState


class BusinessAgent:

    def __init__(self):
        self.gemini = GeminiClient()

    def run(self, state: GraphState):

        report = state.get("report")
        python_result = state.get("python_result")
        sql_result = state.get("sql_result")

        prompt = f"""
You are a senior enterprise data analyst.

Your job is to synthesize the available analysis into a clear,
concise, grounded answer to the user's request.

USER REQUEST:
{state["question"]}

DATASET INSPECTION REPORT:
{report}

PYTHON ANALYSIS RESULT:
{python_result}

SQL ANALYSIS RESULT:
{sql_result}

IMPORTANT RULES:

1. Use only information provided above.

2. Never invent:
   - company information
   - dates
   - industries
   - demographics
   - business context
   - statistics
   - compliance requirements
   - dataset characteristics

3. If information is unavailable, say that it cannot be determined.

4. If Python or SQL results are available, incorporate them into
   the answer.

5. Do not claim that a chart proves something that cannot be
   determined from the supplied information.

6. Focus specifically on answering the user's request.

7. Be concise and professional.

Return the final analytical response.
"""

        answer = self.gemini.generate(prompt)

        state["answer"] = answer

        return state