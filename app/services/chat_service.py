from google import genai
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import os
import json

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class ChatService:

    def __init__(self):
        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def ask(
        self,
        report: dict,
        df: pd.DataFrame,
        question: str
    ) -> str:

        dataset_preview = df.head(100).to_csv(index=False)

        prompt = f"""
You are an expert enterprise data analyst.

Below is a dataset inspection report.

{json.dumps(report, indent=2)}

Below is a preview of the uploaded dataset (first 100 rows).

{dataset_preview}

The user asked:

{question}

Instructions:

- Answer using BOTH the inspection report and the dataset preview.
- If the answer is visible in the preview, answer directly.
- If the question requires data beyond the preview, clearly say that.
- Never invent information.
- Be concise and professional.
"""

        response = self.client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        return response.text