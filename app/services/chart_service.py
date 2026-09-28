from dotenv import load_dotenv
from pathlib import Path

from app.services.gemini_client import GeminiClient

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class ChartService:

    def __init__(self):
        self.gemini = GeminiClient()

    def generate_chart(self, df, question, conversation_history=None):

        columns = list(df.columns)
        dtypes = {
            col: str(dtype)
            for col, dtype in df.dtypes.items()
        }

        preview = df.head(25).to_string(index=False)

        prompt = f"""
You are an expert data visualization engineer.

A pandas DataFrame called df already exists.

Assign the final Plotly figure to a variable named fig. Do not use any other variable name such as result, chart, or plot.

Columns:

{columns}

Data Types:

{dtypes}

Dataset Preview:

{preview}

The user requested:

{question}

Recent conversation context:

{(conversation_history or [])[-6:]}

Generate ONLY valid Python code.

Rules:

- Return ONLY Python code.
- No markdown.
- No explanation.
- Do NOT import anything.
- plotly.express is already available as px.
- pandas is already available as pd.
- Store the final figure in a variable named result.
- Use only columns that appear above.
- Choose an appropriate chart when the follow-up request says "visualize that".

Example:

result = px.scatter(
    df,
    x="Age",
    y="Salary",
    color="Department"
)
"""

        code = self.gemini.generate(prompt)

        code = (
            code
            .replace("```python", "")
            .replace("```", "")
            .strip()
        )

        return code
