from pathlib import Path
from dotenv import load_dotenv
from google import genai
import os

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Hello! Tell me a fun fact about AI."
)

print(response.text)