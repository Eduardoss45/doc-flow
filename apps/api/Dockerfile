FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-core-nogui     \
    libreoffice-writer-nogui   \
    libreoffice-calc-nogui     \
    libreoffice-impress-nogui  \
    libreoffice-draw-nogui     \
    libreoffice-math-nogui     \
    default-jre-headless       \
    fonts-liberation           \
    fonts-dejavu               \
    fonts-noto                 \   
    && apt-get clean           \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip install --upgrade pip
RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY apps/api/pyproject.toml apps/api/poetry.lock ./

RUN poetry install --no-root --only main

COPY apps/api/src ./src

EXPOSE 4000

ENV PYTHONPATH=/app/src