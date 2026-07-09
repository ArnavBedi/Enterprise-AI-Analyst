from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL_NAME = "gpt-5"

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY was not found. Please add it to your .env file."
    )