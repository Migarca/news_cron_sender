import os
import httpx
import schedule
import time
from datetime import date
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(override=True)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def fetch_news_from_llm() -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Dame las 3 noticias más importantes de hoy {date.today()}. Para cada una: titular, resumen en 2 frases y URL fuente.",
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    return response.text.strip()


def send_telegram(message: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    httpx.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"📰 <b>Noticias del {date.today()}</b>\n\n{message}",
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }, timeout=10)


def job():
    news = fetch_news_from_llm()
    send_telegram(news)


if __name__ == "__main__":
    schedule_hour = os.environ.get("SCHEDULE_HOUR", "08:00")
    job()
    schedule.every().day.at(schedule_hour).do(job)
    while True:
        schedule.run_pending()
        time.sleep(30)