import os
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

DAILY_JOB_NAME = "daily_news"
START_TIME = datetime.now()


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


async def send_news(bot, chat_id: int) -> None:
    news = await asyncio.to_thread(fetch_news_from_llm)
    await bot.send_message(
        chat_id=chat_id,
        text=f"📰 <b>Noticias del {date.today()}</b>\n\n{news}",
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


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
        await update.message.reply_text("Formato incorrecto. Usa HH:MM (ej: /hour 09:30)")
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
    app.run_polling()


if __name__ == "__main__":
    main()
