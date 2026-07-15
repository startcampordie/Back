import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5-mini",
)

AI_CANDIDATE_LIMIT = 10
DISPLAY_RESULT_LIMIT = 5
CHAT_MESSAGE_MAX_LENGTH = 100