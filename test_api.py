import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello, can you hear me?",
    )
    print("API Key is Valid!")
    print(response.text)
except Exception as e:
    print("API Key is Invalid or Error Occurred:", e)
