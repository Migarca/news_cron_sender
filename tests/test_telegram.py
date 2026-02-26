import pytest
from main import send_telegram


@pytest.mark.integration
def test_send_telegram_delivers_message():
    """Verifica que send_telegram envía un mensaje correctamente al bot."""
    send_telegram("✅ Test de integración — Telegram funcionando correctamente.")
