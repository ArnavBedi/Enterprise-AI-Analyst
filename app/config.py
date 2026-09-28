from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY was not found. Please add it to your .env file."
    )
