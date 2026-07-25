from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os

from app.services.gemini_client import GeminiClient
from app.tools.python_executor import PythonExecutor

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class PythonService:

    def __init__(self):
        self.gemini = GeminiClient()

    def ask(self, df, question):

        prompt = f"""
    You are an expert Python data analyst.

    A pandas DataFrame called df already exists.

    The user asked:

    {question}

    Generate ONLY valid Python code.

    Rules:

    - Return ONLY Python code.
    - No explanations.
    - No markdown.
    - No ```python.
    - Assume pandas is already imported as pd.
    - plotly.express has already been imported as px.
    - The final object MUST be stored in a variable called result.

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
    Plot salary vs age

    Answer:

    result = px.scatter(
        df,
        x="Age",
        y="Salary",
        color="Department"
    )


    Question:
    Histogram of salaries

    Answer:

    result = px.histogram(
        df,
        x="Salary"
    )
    """

        code = self.gemini.generate(prompt)

        result = PythonExecutor.execute(df, code)

        return code, result