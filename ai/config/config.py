import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


# MODEL = "openai/gpt-oss-120b"

MODEL = "openai/gpt-oss-20b"

API_URL = "http://127.0.0.1:8000"


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)