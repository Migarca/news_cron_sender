import logging
import time
from datetime import date

from google.genai import types

from config import MAX_RETRIES, RETRY_BASE_DELAY, gemini_client


def fetch_news_from_llm() -> str:
    logging.info("Fetching news from LLM...")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = gemini_client.models.generate_content(
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
                    '1️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href="URL">Fuente</a>\n\n'
                    '2️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href="URL">Fuente</a>\n\n'
                    '3️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href="URL">Fuente</a>\n\n'
                    "━━━━━━━━━━━━━━━━━━\n\n"
                    "<b>🇪🇸 NOTICIAS ESPAÑA</b>\n\n"
                    '1️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href="URL">Fuente</a>\n\n'
                    '2️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href="URL">Fuente</a>\n\n'
                    '3️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href="URL">Fuente</a>\n\n'
                    "━━━━━━━━━━━━━━━━━━\n\n"
                    "<b>🤖 NOTICIAS IA</b>\n\n"
                    '1️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href="URL">Fuente</a>\n\n'
                    '2️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href="URL">Fuente</a>\n\n'
                    '3️⃣ <b>Titular</b>\nResumen en 2 frases.\n🔗 <a href="URL">Fuente</a>\n\n'
                    "No añadas ningún texto fuera de este formato."
                ),
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                ),
            )
            logging.info("News fetched successfully")
            return response.text.strip()
        except Exception:
            logging.warning(
                "Gemini API attempt %d/%d failed", attempt, MAX_RETRIES, exc_info=True
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BASE_DELAY * attempt)
    raise RuntimeError("Failed to fetch news after all retries")
