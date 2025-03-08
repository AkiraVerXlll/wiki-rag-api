import os
from dotenv import load_dotenv

load_dotenv()

USER_AGENT = os.getenv("USER_AGENT")
DATA_PATH = "data"
DOCUMENTS_PATH = f"{DATA_PATH}/documents"
SESSIONS_PATH = f"{DATA_PATH}/sessions"
INDICES_PATH = f"{DATA_PATH}/index"
OPENAI_API_TOKEN = os.getenv("OPENAI_API_TOKEN")
REDIS_URL = os.getenv("REDIS_URL")
MODEL = "gpt-3.5-turbo"