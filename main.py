import logging
import os
from datetime import datetime

from telegram.ext import Application, CommandHandler, filters

from bot.handlers import cmd_help, cmd_hour, cmd_news, cmd_status
from bot.sender import scheduled_news
from config import DAILY_JOB_NAME, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN


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
