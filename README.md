# 📌 Doc Flow – Motor Assíncrono de Conversão de Documentos

O **Doc Flow** é um backend para **processamento e conversão assíncrona de documentos**, estruturado como **monólito modular orientado a mensageria**, com comunicação desacoplada entre API e workers e notificações em tempo real via WebSocket.

O foco do projeto é demonstrar:

- Separação rigorosa de responsabilidades
- Processamento assíncrono correto
- Isolamento por cliente sem autenticação
- Controle explícito de recursos
- Efemeridade como regra arquitetural

O sistema não é uma plataforma de gestão documental.
É um **motor técnico de conversão previsível e observável**.

---

## ⚠️ Disclaimer Importante – Variáveis de Ambiente (`.env`)

> O funcionamento do sistema depende obrigatoriamente da configuração correta do arquivo `.env`.

Antes de executar localmente:

1. Criar o `.env` a partir do `.env.example`
2. Garantir o preenchimento correto de todas as variáveis

Itens críticos:

- URL do **PostgreSQL**
- URL do **Redis**
- URL do **RabbitMQ**
- Diretórios de storage
- Configuração de CORS (`ALLOWED_ORIGINS`)
- Configuração do Socket.IO
- Limites de upload e TTL

Falhas comuns decorrentes de má configuração:

- Workers não processam jobs
- Eventos não chegam via WebSocket
- Erros silenciosos de conexão
- Rate limit não funcional
- Falhas na persistência

---

## 🧱 Visão Geral da Arquitetura

```
Frontend (Next.js)
        │
        │ HTTP + WebSocket
        ▼
Flask API + Socket.IO
        │
        ├── PostgreSQL (estado dos jobs)
        │
        ├── RabbitMQ (fila de tarefas)
        │
        └── Redis (pub/sub + cache)
                    │
                    ▼
              Celery Workers
                    │
                    ▼
                Storage Local
```

### Tecnologias Principais

- Flask
- Celery
- RabbitMQ
- Redis
- PostgreSQL
- Docker

---

## 🔐 Modelo de Segurança

O sistema **não possui autenticação**.

O isolamento é feito exclusivamente por:

- `client_id` (UUID v4)
- Cookie HTTP-only
- Validação de correspondência no download
- Isolamento físico de diretórios
- Limite de armazenamento por cliente
- Expiração automática

### Rate Limiting

- 10 requisições por segundo por IP
- Implementado na camada HTTP

### Garantias

- Não há enumeração de jobs
- UUID evita previsibilidade
- Downloads exigem correspondência de `client_id`

---

## 📦 Domínio de Processamento

### Estados de Job

- `PENDING`
- `PROCESSING`
- `DONE`
- `FAILED`

### Estrutura Persistida

Tabela `DocumentJob`:

- `id (UUID)`
- `client_id`
- `status`
- `input_filename`
- `input_path`
- `output_format`
- `output_path`
- `error_message`
- `created_at`
- `processed_at`
- `expires_at`

O banco representa apenas o ciclo de vida técnico.

---

## 🔁 Fluxo Assíncrono

1. Upload via API
2. Arquivo salvo em `/storage/input/{client_id}`
3. Job persistido no banco
4. Metadados enviados ao RabbitMQ
5. Worker processa
6. Output movido para `/storage/output/{client_id}`
7. Status atualizado
8. Evento publicado no Redis
9. API emite evento via WebSocket

### Regra Estrutural

> Arquivos nunca trafegam pela fila.

A fila transporta apenas metadados.

---

## 🔔 Notificações em Tempo Real

- Workers publicam eventos no Redis
- API consome via pub/sub
- Emissão via Socket.IO para `room(client_id)`

Eventos:

- `job_processing`
- `job_done`
- `job_failed`

Sem polling contínuo.

---

## 🗃️ Estratégia de Armazenamento

Estrutura física:

```
/storage/input/{client_id}
/storage/output/{client_id}
```

### Limites

- 250 MB por `client_id`
- Soma de input + output
- Upload bloqueado quando limite atingido

### Expiração

- TTL padrão: 24h
- Tarefa periódica remove:
  - Registros
  - Arquivos físicos
  - Libera cota

Efemeridade é comportamento padrão.

---

## 🔄 Conversões Suportadas

### Dados tabulares

- CSV ↔ Excel ↔ JSON
- `pandas`

### Texto estruturado

- Markdown ↔ HTML ↔ TXT
- `markdown`, `markitdown`

### TXT → PDF

- `ReportLab`, `fpdf`

### PDF → TXT

- `pdfplumber`, `PyPDF2`, `tika`

### Office → visão

- DOCX / PPTX → PDF / Markdown
- `python-docx`, `docling`

Conversões dependentes de layout visual complexo não fazem parte do escopo.

---

## 🧪 Testes Automatizados

Testes focados na camada de domínio:

- Services
- Validações
- Controle de cota
- Expiração
- Regras de status

Estratégia:

- Repositórios mockados
- Simulação de workers
- Testes de erro e fluxos felizes

Objetivo: confiabilidade estrutural, não cobertura artificial.

---

## 📑 Documentação da API (Swagger)

A API está documentada via:

- flask-smorest
- marshmallow
- Swagger UI

### Acesso

```
http://localhost:4000/docs/swagger
```

### O que está documentado

- Todas as rotas HTTP
- Schemas de request/response
- Parâmetros de rota
- Status codes
- Validações

O Swagger representa o contrato real da API.

Não documenta eventos internos de mensageria.

---

## 🐳 Infraestrutura & Docker

Serviços orquestrados via Docker Compose:

- Web
- API
- Worker
- Celery Beat
- PostgreSQL
- Redis
- RabbitMQ

Execução:

```bash
docker compose up --build
```

---

## 🗄️ Banco de Dados & Migrations

- SQLAlchemy 2.0
- Alembic
- `synchronize` não utilizado
- Migrations explícitas

Banco único com separação lógica por domínio.

---

## ▶️ Execução Local

> backend

```bash
poetry install
poetry run start-api
poetry run start-worker
poetry run celery -A src.workers.celery_app beat --loglevel=info
```

> frontend

```bash
npm run dev
```

Pré-requisitos:

- Python 3.11+
- PostgreSQL
- Redis
- RabbitMQ
- `.env` configurado

---

## 🧠 Decisões Técnicas

- Monólito modular (evita complexidade prematura)
- Mensageria para desacoplamento
- UUID para evitar enumeração
- TTL obrigatório
- Storage isolado por cliente
- WebSocket fora do fluxo HTTP
- Arquivos fora da fila

---

## ⚠️ Trade-offs

- Sem autenticação (decisão consciente)
- Limite rígido de 250 MB
- Conversões complexas fora do escopo
- Observabilidade básica (logging estruturado)

---

## 🚀 Melhorias Futuras

- Retry + DLQ no RabbitMQ
- Cache Redis para consultas frequentes
- Observabilidade avançada (OpenTelemetry)
- Testes E2E
- Storage externo (S3-compatible)
- Métricas Prometheus

---

## 🎯 Objetivo do Projeto

Demonstrar como um sistema real de processamento de documentos deve ser estruturado para:

- Escalar horizontalmente
- Controlar recursos
- Evitar acoplamento
- Manter previsibilidade operacional
- Operar com efemeridade como padrão

O foco é engenharia sólida, não expansão indiscriminada de funcionalidades.
