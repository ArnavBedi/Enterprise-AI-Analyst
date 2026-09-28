from app.services.gemini_client import GeminiClient
from app.tools.python_executor import PythonExecutor


class PythonService:

    def __init__(self):
        self.gemini = GeminiClient()

    def ask(self, df, question, conversation_history=None):

        prompt = f"""
You are the Python computation agent in a multi-agent
enterprise data analysis system.

A pandas DataFrame called df already exists.

The user's overall request is:

{question}

Recent conversation context:

{(conversation_history or [])[-6:]}

Your responsibility is ONLY to perform the numerical,
statistical, filtering, aggregation, or tabular analysis
required by the request.

Other specialized agents handle visualization and explanation.

Generate ONLY valid Python code.

Rules:

- Return ONLY Python code.
- No explanations.
- No markdown.
- No ```python.
- Assume pandas is already imported as pd.
- The DataFrame is already available as df.
- The final analytical output MUST be stored in a variable
  called result.

IMPORTANT:

- Do NOT create charts or visualizations.
- Do NOT use Plotly.
- Do NOT use px.
- Do NOT provide business explanations.
- Do NOT generate written summaries.
- Do NOT perform work that belongs to another agent.
- Only calculate or extract the information needed from df.

Examples:

Question:
Average salary

Answer:

result = df["Salary"].mean()


Question:
Employees older than 30

Answer:

result = df[df["Age"] > 30]


Question:
Salary by department

Answer:

result = (
    df.groupby("Department")["Salary"]
    .mean()
)


Question:
Calculate average salary and plot salary vs age

Answer:

result = df["Salary"].mean()


Question:
Calculate average salary, plot salary vs age,
and explain the result

Answer:

result = df["Salary"].mean()
"""

        code = self.gemini.generate(prompt)

        result = PythonExecutor.execute(
            df,
            code
        )

        return code, result
