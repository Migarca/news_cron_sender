import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from google import genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv(override=True)

gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = int(os.environ["TELEGRAM_CHAT_ID"])

MAX_RETRIES = 3
RETRY_BASE_DELAY = 5

DAILY_JOB_NAME = "daily_news"
START_TIME = datetime.now()
