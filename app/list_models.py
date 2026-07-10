from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

for model in client.models.list():
    methods = getattr(model, "supported_actions", None) or getattr(model, "supported_generation_methods", [])
    print(f"{model.name}")
    print(f"  Supported: {methods}")
    print()