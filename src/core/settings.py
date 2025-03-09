import os
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = "data"
DOCUMENTS_PATH = f"{DATA_PATH}/documents"
SESSIONS_PATH = f"{DATA_PATH}/sessions"
INDICES_PATH = f"{DATA_PATH}/indices"
LOGS_PATH = "/logs"
MODEL = "gpt-3.5-turbo"

USER_AGENT = os.getenv("USER_AGENT")
OPENAI_API_TOKEN = os.getenv("OPENAI_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")

