import os
import time
import asyncio
import logging
from datetime import date, datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)

load_dotenv(override=True)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = int(os.environ["TELEGRAM_CHAT_ID"])

MAX_RETRIES = 3
RETRY_BASE_DELAY = 5

DAILY_JOB_NAME = "daily_news"
START_TIME = datetime.now()


def fetch_news_from_llm() -> str:
    logging.info("Fetching news from LLM...")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
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


async def send_news(bot, chat_id: int) -> None:
    try:
        news = await asyncio.to_thread(fetch_news_from_llm)
    except Exception:
        logging.error("Failed to fetch news from Gemini", exc_info=True)
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="⚠️ Error al obtener las noticias. Inténtalo de nuevo más tarde.",
            )
        except Exception:
            logging.error("Failed to send error notification", exc_info=True)
        return

    header = f"📰 <b>Noticias del {date.today()}</b>"
    sections = [s.strip() for s in news.split("━━━━━━━━━━━━━━━━━━") if s.strip()]

    try:
        await bot.send_message(chat_id=chat_id, text=header, parse_mode="HTML")
        for section in sections:
            await bot.send_message(
                chat_id=chat_id,
                text=section,
                parse_mode="HTML",
                disable_web_page_preview=True,
            )
    except Exception:
        logging.error("Failed to send news via Telegram", exc_info=True)
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="⚠️ Error al enviar las noticias. Inténtalo de nuevo más tarde.",
            )
        except Exception:
            logging.error("Failed to send error notification", exc_info=True)


async def scheduled_news(context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("Scheduled job started")
    await send_news(context.bot, TELEGRAM_CHAT_ID)
    logging.info("Scheduled job finished")


async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info("/news command received")
    await update.message.reply_text("Buscando noticias...")
    await send_news(context.bot, update.effective_chat.id)


async def cmd_hour(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Uso: /hour HH:MM (ej: /hour 09:30)")
        return
    try:
        new_time = datetime.strptime(context.args[0], "%H:%M").time()
    except ValueError:
        await update.message.reply_text(
            "Formato incorrecto. Usa HH:MM (ej: /hour 09:30)"
        )
        return

    jobs = context.job_queue.get_jobs_by_name(DAILY_JOB_NAME)
    for job in jobs:
        job.schedule_removal()

    context.job_queue.run_daily(scheduled_news, time=new_time, name=DAILY_JOB_NAME)
    logging.info(f"Schedule changed to {context.args[0]}")
    await update.message.reply_text(f"Hora cambiada a {context.args[0]}")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uptime = datetime.now() - START_TIME
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)

    jobs = context.job_queue.get_jobs_by_name(DAILY_JOB_NAME)
    next_run = jobs[0].next_t.strftime("%H:%M") if jobs else "No programado"

    await update.message.reply_text(
        f"<b>Estado del bot</b>\n\n"
        f"Uptime: {hours}h {minutes}m\n"
        f"Próximo envío: {next_run}",
        parse_mode="HTML",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "<b>Comandos disponibles</b>\n\n"
        "/news - Enviar noticias ahora\n"
        "/hour HH:MM - Cambiar hora del envío diario\n"
        "/status - Ver estado del bot\n"
        "/help - Ver esta ayuda",
        parse_mode="HTML",
    )


def main() -> None:
    schedule_hour = os.environ.get("SCHEDULE_HOUR", "08:00")
    schedule_time = datetime.strptime(schedule_hour, "%H:%M").time()

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    chat_filter = filters.Chat(chat_id=TELEGRAM_CHAT_ID)
    app.add_handler(CommandHandler("news", cmd_news, filters=chat_filter))
    app.add_handler(CommandHandler("hour", cmd_hour, filters=chat_filter))
    app.add_handler(CommandHandler("status", cmd_status, filters=chat_filter))
    app.add_handler(CommandHandler("help", cmd_help, filters=chat_filter))

    app.job_queue.run_daily(scheduled_news, time=schedule_time, name=DAILY_JOB_NAME)
    app.job_queue.run_once(scheduled_news, when=0)

    logging.info(f"Bot started. Scheduled daily at {schedule_hour}")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
