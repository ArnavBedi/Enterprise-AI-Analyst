from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os

from app.tools.python_executor import PythonExecutor

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class PythonService:

    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def ask(self, df, question):

        prompt = f"""
You are a Python data analyst.

A pandas DataFrame called df already exists.

The user asked:

{question}

Return ONLY ONE valid pandas expression.

Rules:

- Return ONLY Python code.
- Do NOT explain anything.
- Do NOT use markdown.
- Do NOT use ```python.
- Do NOT assign variables.
- The expression must evaluate directly.

Examples:

Question:
How many rows?

Answer:
len(df)

Question:
Average salary?

Answer:
df["Salary"].mean()

Question:
Highest salary?

Answer:
df.loc[df["Salary"].idxmax()]
"""

        response = self.client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        code = response.text.strip()

        # Remove markdown fences if Gemini accidentally adds them
        code = code.replace("```python", "")
        code = code.replace("```", "")
        code = code.strip()

        result = PythonExecutor.execute(df, code)

        return code, result