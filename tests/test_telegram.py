import pytest
from telegram import Bot


@pytest.mark.integration
def test_telegram_bot_token_is_valid():
    """Verifica que el token del bot de Telegram es válido."""
    import os
    bot = Bot(token=os.environ["TELEGRAM_TOKEN"])
    import asyncio
    me = asyncio.run(bot.get_me())
    assert me.is_bot
