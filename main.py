import os
import logging
import httpx
import schedule
import time
from datetime import date
from dotenv import load_dotenv
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

load_dotenv(override=True)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def fetch_news_from_llm() -> str:
    logging.info("Fetching news from LLM...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            f"Dame las noticias más importantes, relevantes y de mayor interés público de hoy {date.today()}. "
            "Dame exactamente 3 a nivel global, 3 a nivel nacional (España) y 3 relacionadas con Inteligencia Artificial. "
            "Las noticias deben estar publicadas en las últimas 24 horas. "
            "Deben provenir únicamente de medios reconocidos y confiables (ej. BBC, Reuters, AP, AFP, The Guardian, El País, La Voz de Galicia, etc.). "
            "Cada noticia debe estar confirmada por al menos dos fuentes independientes y ser verificable. "
            "Selecciona únicamente noticias con alto impacto político, económico, social o geopolítico. "
            "Descarta sucesos aislados, ciberataques locales, crímenes individuales o noticias de bajo impacto estratégico. "
            "El resumen debe tener exactamente 2 frases claras y neutrales, sin opiniones, sin lenguaje sensacionalista y sin clickbait. "
            "Devuelve SOLO el texto formateado en HTML de Telegram siguiendo EXACTAMENTE esta estructura:\n\n"
            "<b>🌍 NOTICIAS GLOBALES</b>\n\n"
            "1️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href=\"URL\">Fuente</a>\n\n"
            "2️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href=\"URL\">Fuente</a>\n\n"
            "3️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href=\"URL\">Fuente</a>\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "<b>🇪🇸 NOTICIAS ESPAÑA</b>\n\n"
            "1️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href=\"URL\">Fuente</a>\n\n"
            "2️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href=\"URL\">Fuente</a>\n\n"
            "3️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href=\"URL\">Fuente</a>\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "<b>🤖 NOTICIAS IA</b>\n\n"
            "1️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href=\"URL\">Fuente</a>\n\n"
            "2️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href=\"URL\">Fuente</a>\n\n"
            "3️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href=\"URL\">Fuente</a>\n\n"
            "No añadas ningún texto fuera de este formato."
        ),
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    logging.info("News fetched successfully")
    return response.text.strip()


def send_telegram(message: str) -> None:
    logging.info("Sending message to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    httpx.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"📰 <b>Noticias del {date.today()}</b>\n\n{message}",
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }, timeout=10)
    logging.info("Message sent to Telegram")


def job():
    logging.info("Job started")
    news = fetch_news_from_llm()
    send_telegram(news)
    logging.info("Job finished")


if __name__ == "__main__":
    schedule_hour = os.environ.get("SCHEDULE_HOUR", "08:00")
    logging.info(f"Scheduled daily at {schedule_hour}")
    job()
    schedule.every().day.at(schedule_hour).do(job)
    while True:
        schedule.run_pending()
        time.sleep(30)