FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

RUN useradd --create-home --shell /bin/bash --uid 1000 appuser && \
    mkdir -p /ms-playwright && \
    chown -R appuser:appuser /app /ms-playwright

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry

COPY apps/api/pyproject.toml apps/api/poetry.lock ./

FROM base AS api

RUN poetry install --no-root --only main,api

COPY apps/api/src ./src

RUN mkdir -p /app/src/app/infra/storage/output && \
    chown -R appuser:appuser /app

USER appuser
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

RUN poetry install --no-root --only main,worker

COPY apps/api/src ./src

RUN python -m playwright install chromium && \
    chown -R appuser:appuser /app /ms-playwright

USER appuser
CMD ["poetry", "run", "start-worker"]

FROM base AS beat

RUN poetry install --no-root --only main

COPY apps/api/src ./src

RUN chown -R appuser:appuser /app

USER appuser
CMD ["poetry", "run", "celery", "-A", "src.app.workers.celery_app", "beat", "--loglevel=info"]