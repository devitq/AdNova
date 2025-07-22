# Stage 1: Install dependencies
FROM docker.io/python:3.13-alpine3.22 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2 \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml .

RUN uv sync --no-dev --no-install-project --no-cache


# Stage 2: Start the application
FROM docker.io/python:3.13-alpine3.22

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

COPY . .

RUN adduser -D -g '' app && chown -R app:app ./

USER app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=2 \
    PATH="/opt/venv/bin:$PATH"

CMD [ "python", "main.py" ]
