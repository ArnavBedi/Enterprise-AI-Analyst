from .gemini_client import GeminiClient
import json


class AnalystService:

    def __init__(self):
        self.gemini = GeminiClient()

    def analyze(self, report: dict):

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

        return self.gemini.generate(prompt)