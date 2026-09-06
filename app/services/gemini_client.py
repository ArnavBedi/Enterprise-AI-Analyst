from google import genai
from google.genai.errors import ServerError
from dotenv import load_dotenv
from pathlib import Path
import os
import time
import json


load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


class GeminiClient:

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

        self.models = [
            "gemini-3.5-flash",
            "gemini-3.1-flash-lite",
            "gemini-2.5-flash"
        ]

    def generate(self, prompt: str):

        last_error = None

        for model in self.models:

            for attempt in range(3):

                try:

                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt
                    )

                    return response.text

                except ServerError as e:

                    last_error = e

                    wait = 2 ** attempt

                    print(
                        f"{model} busy... retrying in {wait}s"
                    )

                    time.sleep(wait)

                except Exception as e:

                    last_error = e
                    break

        raise last_error

    def generate_json(self, prompt: str, schema):

        last_error = None

        for model in self.models:

            for attempt in range(3):

                try:

                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config={
                            "response_mime_type": "application/json",
                            "response_schema": schema
                        }
                    )

                    if getattr(response, "parsed", None) is not None:
                        return response.parsed

                    return json.loads(response.text)

                except ServerError as e:

                    last_error = e

                    wait = 2 ** attempt

                    print(
                        f"{model} busy... retrying in {wait}s"
                    )

                    time.sleep(wait)

                except Exception as e:

                    last_error = e
                    break

        raise last_error