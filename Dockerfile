FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY main.py config.py ./
COPY bot/ bot/
COPY services/ services/

CMD ["uv", "run", "python", "main.py"]