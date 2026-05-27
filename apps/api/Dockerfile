FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN apt-get update && apt-get install -y --no-install-recommends \
    \
    # LibreOffice
    libreoffice-core-nogui \
    libreoffice-writer-nogui \
    libreoffice-calc-nogui \
    libreoffice-impress-nogui \
    libreoffice-draw-nogui \
    libreoffice-math-nogui \
    default-jre-headless \
    \
    # Chromium / Playwright deps
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
    \
    # Fonts
    fonts-liberation \
    fonts-dejavu \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY apps/api/pyproject.toml apps/api/poetry.lock ./

RUN poetry install --no-root --only main

COPY apps/api/src ./src

# instala chromium do playwright
RUN python -m playwright install chromium

EXPOSE 4000

ENV PYTHONPATH=/app/src