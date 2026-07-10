from google import genai
from dotenv import load_dotenv
from pathlib import Path
import os
import json

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class AnalystService:

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def analyze(self, report: dict) -> str:

        prompt = f"""
You are a senior enterprise data analyst.

Below is a dataset inspection report.

{json.dumps(report, indent=2)}

Please provide:

1. Executive Summary

2. Data Quality Issues

3. Interesting Patterns

4. Business Insights

5. Recommended Machine Learning Tasks

Keep the response professional.
"""

        response = self.client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        return response.text