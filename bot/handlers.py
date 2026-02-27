import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from bot.sender import send_news
from config import DAILY_JOB_NAME, START_TIME


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

    from bot.sender import scheduled_news

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
