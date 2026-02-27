import asyncio
import logging
from datetime import date

from telegram.ext import ContextTypes

from config import TELEGRAM_CHAT_ID
from services.news import fetch_news_from_llm


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
