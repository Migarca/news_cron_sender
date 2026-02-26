# news_sender_cron

Bot que cada mañana a las 8:00 busca las 3 noticias más relevantes del día usando Gemini con Google Search y las envía a Telegram.

## Stack

- **Python 3.12** + **uv** para gestión de dependencias
- **Gemini 2.0 Flash** con grounding de Google Search
- **Telegram Bot API** para la notificación
- **Docker** para el despliegue

## Requisitos

- Docker y Docker Compose
- Una API key de [Google AI Studio](https://aistudio.google.com) (gratis)
- Un bot de Telegram

## Setup

### 1. Clonar e inicializar dependencias

```bash
git clone <repo>
cd news_sender_cron
uv init --no-readme
uv add httpx schedule google-genai
```

### 2. Crear el bot de Telegram

1. Abre Telegram y busca `@BotFather`
2. Ejecuta `/newbot` y sigue los pasos
3. Copia el token que te da

Para obtener tu `TELEGRAM_CHAT_ID`:
1. Manda cualquier mensaje a tu bot
2. Visita `https://api.telegram.org/botTU_TOKEN/getUpdates`
3. Busca el campo `"chat":{"id": XXXXXXX}`

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus valores:

```env
GEMINI_API_KEY=tu_gemini_api_key
TELEGRAM_TOKEN=tu_bot_token
TELEGRAM_CHAT_ID=tu_chat_id
```

### 4. Arrancar

```bash
docker compose up -d --build
```

El bot ejecuta el job inmediatamente al arrancar para verificar que todo funciona, y después lo programa diariamente a las 8:00.

## Desarrollo local

```bash
uv run python main.py
```

## Estructura

```
news_sender_cron/
├── main.py              # lógica principal
├── pyproject.toml       # dependencias
├── uv.lock              # lockfile (generado por uv)
├── .python-version      # versión de Python (generado por uv)
├── Dockerfile
├── docker-compose.yml
├── .env                 # secrets (no commitear)
├── .env.example         # plantilla
└── .gitignore
```