import os
from configparser import ConfigParser
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

CONFIG_FILE = Path(__file__).parent / "config.ini"

config = ConfigParser()
config.read(CONFIG_FILE, encoding="utf-8")

API_URL = config["api"]["url"]
MODEL = config["groq"]["model"]

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)