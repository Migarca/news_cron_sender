import os
import pytest
from google import genai


@pytest.mark.integration
def test_gemini_api_key_is_valid():
    """Verifica que la API key de Gemini es válida y responde correctamente."""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello, can you hear me?",
    )
    assert response.text
