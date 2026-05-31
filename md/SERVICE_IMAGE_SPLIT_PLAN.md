# Ordem de Desenvolvimento - Separacao de Imagens por Alvo

## Objetivo

Separar as imagens de execucao do monolito por responsabilidade operacional:

- API HTTP
- Worker de conversao
- Celery Beat

Isso nao transforma o projeto em microservicos.

A ideia e manter o mesmo codigo, o mesmo banco, o mesmo broker e o mesmo dominio, mas gerar imagens menores e mais adequadas para cada processo.

---

## Problema Atual

Hoje `backend`, `worker` e `celery` usam o mesmo `apps/api/Dockerfile`.

Esse Dockerfile instala tudo:

- Flask/API
- Celery
- LibreOffice
- Chromium/Playwright
- fontes pesadas
- dependencias de conversao

Consequencias:

- API carrega runtime de conversao que nao usa.
- Celery Beat carrega Chromium/LibreOffice sem necessidade.
- Worker fica acoplado a dependencias de API.
- Imagens ficam maiores.
- Rebuilds ficam mais lentos.
- A superficie operacional cresce para servicos simples.

---

## Principio Arquitetural

Separar por alvo de runtime, nao por dominio.

O codigo continua sendo monolito modular:

```text
apps/api/src/app
```

Mas os containers passam a ser especializados:

```text
api image       -> HTTP, WebSocket, Swagger, enqueue jobs
worker image    -> conversoes pesadas
beat image      -> agendamento e cleanup
```

---

## Fase 1 - Mapear Dependencias Por Processo

Antes de criar novos Dockerfiles, classificar dependencias.

### API HTTP

Precisa de:

- Flask
- flask-smorest
- flask-cors
- flask-limiter
- flask-socketio
- SQLAlchemy
- psycopg
- Redis client
- Celery client para enfileirar tasks
- Marshmallow

Nao deveria precisar de:

- Chromium
- Playwright browsers
- LibreOffice
- Pygments
- markdown-it-py
- pdfplumber
- pandas/openpyxl, se apenas o worker converte

### Worker de Conversao

Precisa de:

- Celery
- SQLAlchemy
- psycopg
- Redis/RabbitMQ
- pandas/openpyxl
- pdfplumber
- markitdown/docx
- LibreOffice
- Playwright/Chromium
- markdown-it-py
- Pygments
- Bleach
- BeautifulSoup
- Requests
- Jinja2
- fontes

### Celery Beat

Precisa de:

- Celery
- SQLAlchemy
- psycopg
- Redis/RabbitMQ
- codigo de cleanup

Nao deveria precisar de:

- Chromium
- Playwright browsers
- LibreOffice
- conversores pesados

---

## Fase 2 - Separar Grupos de Dependencias no Poetry

Manter dependencias comuns em `main`.

Criar grupos opcionais por alvo:

```toml
[tool.poetry.group.api.dependencies]
flask = "..."
flask-smorest = "..."
flask-cors = "..."
flask-limiter = "..."
flask-socketio = "..."
marshmallow = "..."

[tool.poetry.group.worker.dependencies]
pandas = "..."
openpyxl = "..."
pdfplumber = "..."
markitdown = {version = "...", extras = ["docx"]}
markdown-it-py = "..."
pygments = "..."
playwright = "..."
bleach = "..."
beautifulsoup4 = "..."
requests = "..."
jinja2 = "..."

[tool.poetry.group.beat.dependencies]
celery = {version = "...", extras = ["redis"]}
```

Dependencias comuns continuam em `main`:

```toml
python-dotenv = "..."
celery = {version = "...", extras = ["redis"]}
psycopg = {version = "...", extras = ["binary"]}
sqlalchemy = "..."
```

Observacao: a separacao pode ser incremental. Primeiro criar grupos sem mover tudo de uma vez; depois reduzir cada imagem.

---

## Fase 3 - Criar Dockerfile Base

Criar um Dockerfile base leve para instalar Poetry e copiar o codigo.

Exemplo:

```dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src

RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY apps/api/pyproject.toml apps/api/poetry.lock ./
```

Esse stage vira base para API, worker e beat.

---

## Fase 4 - Criar Imagem da API

Objetivo: imagem pequena, sem Chromium e sem LibreOffice.

Exemplo:

```dockerfile
FROM base AS api

RUN poetry install --no-root --only main,api

COPY apps/api/src ./src

EXPOSE 4000

CMD ["poetry", "run", "start-api"]
```

Regra:

- API pode importar `celery_app` para enfileirar.
- API nao deve importar conversores diretamente.
- Evitar imports de worker em `factory.py`, se eles puxarem dependencias pesadas.

---

## Fase 5 - Criar Imagem do Worker

Objetivo: imagem pesada somente onde o peso e necessario.

Exemplo:

```dockerfile
FROM base AS worker

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice-core-nogui \
    libreoffice-writer-nogui \
    libreoffice-calc-nogui \
    libreoffice-impress-nogui \
    default-jre-headless \
    wget \
    curl \
    ca-certificates \
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

RUN python -m playwright install chromium

CMD ["poetry", "run", "start-worker"]
```

Regra:

- Worker pode carregar conversores pesados.
- Worker deve ter limites de memoria/CPU no Compose.
- Worker pode futuramente ser dividido por fila, sem dividir o dominio.

---

## Fase 6 - Criar Imagem do Celery Beat

Objetivo: imagem pequena para agendamento.

Exemplo:

```dockerfile
FROM base AS beat

RUN poetry install --no-root --only main,beat

COPY apps/api/src ./src

CMD ["poetry", "run", "celery", "-A", "src.app.workers.celery_app", "beat", "--loglevel=info"]
```

Regra:

- Beat nao deve importar conversores pesados.
- Beat apenas agenda tarefas.
- Se uma tarefa agendada precisar de conversor pesado, ela deve ser executada pelo worker, nao pelo beat.

---

## Fase 7 - Atualizar docker-compose

Usar o mesmo Dockerfile com targets diferentes.

Exemplo:

```yaml
backend:
  build:
    context: .
    dockerfile: apps/api/Dockerfile
    target: api
  command: poetry run start-api

worker:
  build:
    context: .
    dockerfile: apps/api/Dockerfile
    target: worker
  command: poetry run start-worker
  shm_size: "1gb"
  mem_limit: 1g
  cpus: 1.0

celery:
  build:
    context: .
    dockerfile: apps/api/Dockerfile
    target: beat
  command: poetry run celery -A src.app.workers.celery_app beat --loglevel=info
```

Resultado esperado:

- API menor.
- Beat menor.
- Worker continua pesado, mas por motivo correto.

---

## Fase 8 - Ajustar Imports Para Evitar Dependencias Pesadas na API

Essa fase e critica.

Mesmo com imagem separada, se a API importar um modulo que importa Playwright, o container da API quebra.

Verificar:

```text
factory.py
routes.py
document_service.py
repositories/
domain/
workers/celery_app.py
```

Regra:

- API pode importar task Celery por nome ou assinatura.
- API nao deve importar `app.workers.converters.*`.
- Conversores devem ser importados dinamicamente apenas dentro do worker.

Ponto atual positivo:

```python
process_conversion.delay(...)
```

Ponto de atencao:

```python
from app.workers.tasks.conversion_worker import process_conversion
```

Isso importa o modulo do worker dentro da rota. Funciona, mas pode puxar dependencia indevida se o modulo crescer.

Evolucao recomendada:

```python
celery.send_task(
    "process_conversion",
    args=[str(job.id), str(client_id)],
)
```

Assim a API enfileira por nome e nao importa o modulo do worker.

---

## Fase 9 - Separar Variaveis Por Processo

API:

```env
DATABASE_URL=...
RABBITMQ_URL=...
REDIS_URL=...
ALLOWED_ORIGINS=...
```

Worker:

```env
DATABASE_URL=...
RABBITMQ_URL=...
REDIS_URL=...
ALLOWED_IMAGE_DOMAINS=...
ALLOWED_IMAGE_TYPES=...
MAX_IMAGE_SIZE=...
MAX_MARKDOWN_SIZE=...
MAX_RENDERED_HTML_SIZE=...
```

Beat:

```env
DATABASE_URL=...
RABBITMQ_URL=...
REDIS_URL=...
TIMEZONE=...
```

Regra:

- Variavel de conversao fica no worker.
- Variavel HTTP/CORS fica na API.
- Variavel de agendamento fica no beat.

---

## Fase 10 - Testes de Regressao

Validar depois da separacao:

1. API sobe sem Chromium instalado.
2. Beat sobe sem Chromium/LibreOffice instalado.
3. Worker converte `markdown_to_pdf`.
4. Worker converte `docx_to_pdf`.
5. API consegue enfileirar job sem importar conversor.
6. Cleanup continua rodando via beat.
7. Docker Compose ainda compartilha o volume `storage`.
8. Logs mostram qual processo falhou quando algo quebra.

---

## Ordem Recomendada

1. Criar targets `api`, `worker`, `beat` no Dockerfile.
2. Atualizar Compose para usar `target`.
3. Garantir que API nao importa conversores.
4. Mover variaveis especificas para o servico correto.
5. Separar grupos Poetry incrementalmente.
6. Adicionar limites de recursos no worker.
7. Criar worker dedicado para Markdown/PDF somente se houver carga real.

---

## O Que Nao Fazer Agora

- Nao separar repositorios.
- Nao criar microservicos.
- Nao separar banco.
- Nao criar Kubernetes.
- Nao duplicar codigo.
- Nao criar filas especializadas antes de medir uso real.

---

## Definicao de Pronto

A separacao esta boa quando:

- API builda sem instalar Chromium.
- Beat builda sem instalar Chromium e LibreOffice.
- Worker continua com as dependencias pesadas.
- O fluxo HTTP -> job -> worker -> output continua igual.
- O monolito continua sendo uma unica aplicacao modular.
- O custo operacional fica alinhado ao processo que realmente usa cada dependencia.

