FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN pip install --upgrade pip \
    && pip install poetry \
    && poetry config virtualenvs.create false

COPY apps/api/pyproject.toml apps/api/poetry.lock ./
RUN poetry install --no-root --only main

COPY apps/api/src ./src

FROM base AS api

EXPOSE 4000

CMD ["poetry", "run", "start-api"]

FROM base AS worker

RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-core-nogui \
    libreoffice-writer-nogui \
    libreoffice-calc-nogui \
    libreoffice-impress-nogui \
    libreoffice-draw-nogui \
    libreoffice-math-nogui \
    default-jre-headless \
    wget \
    curl \
    ca-certificates \
    xvfb \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    fonts-liberation \
    fonts-dejavu \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m playwright install chromium

CMD ["poetry", "run", "start-worker"]

FROM base AS beat

CMD ["poetry", "run", "celery", "-A", "src.app.workers.celery_app", "beat", "--loglevel=info"]