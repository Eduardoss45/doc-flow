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

## 🐳 Infraestrutura & Docker

O projeto é totalmente containerizado utilizando **Docker** e orquestrado via **Docker Compose**, garantindo:

- Isolamento de dependências
- Reprodutibilidade do ambiente
- Inicialização previsível
- Execução uniforme entre ambientes

Todos os serviços são executados como containers independentes, comunicando-se exclusivamente via rede interna do Docker.

---

### Serviços Orquestrados

O `docker-compose.yml` define os seguintes serviços:

- **Frontend (Next.js)**
- **API (Flask + Socket.IO)**
- **Worker (Celery)**
- **Celery Beat**
- **PostgreSQL**
- **Redis**
- **RabbitMQ**

Arquiteturalmente:

- A **API** é responsável pelo HTTP e WebSocket.
- O **Worker** executa tarefas assíncronas.
- O **Beat** agenda tarefas periódicas (ex.: expiração de arquivos).
- O **RabbitMQ** atua como broker.
- O **Redis** é utilizado para pub/sub e backend de resultados.
- O **PostgreSQL** mantém o estado dos jobs.

Todos os serviços compartilham a mesma rede Docker interna.

---

### Execução com Docker

Para subir todo o ambiente:

```bash
docker compose up --build
```

Esse comando:

- Constrói as imagens necessárias
- Cria a rede interna
- Inicializa todos os containers
- Conecta automaticamente os serviços pelos nomes definidos no compose

Após inicialização:

- API disponível em `http://localhost:4000`
- Swagger disponível em `http://localhost:4000/docs/swagger`
- Frontend disponível em `http://localhost:3000`

---

### Comunicação Interna

A comunicação entre serviços ocorre exclusivamente via hostname interno do Docker:

- `postgres`
- `redis`
- `rabbitmq`
- `api`
- `worker`

Exemplo de URL interna válida:

```
amqp://guest:guest@rabbitmq:5672
redis://redis:6379/0
postgresql+psycopg://user:pass@postgres:5432/db
```

Não há dependência de `localhost` dentro dos containers.

---

### Health Checks & Dependências

Os serviços utilizam:

- `depends_on`
- Inicialização controlada por ordem lógica

No entanto:

> A disponibilidade real é garantida por retry interno (ex.: Celery e SQLAlchemy), não apenas por dependência declarativa.

Isso evita falhas prematuras caso algum serviço ainda esteja inicializando.

---

### Persistência de Dados

Volumes são utilizados para:

- Persistência do PostgreSQL
- Persistência do RabbitMQ
- Diretório `/storage` (input/output de arquivos)

Isso garante que:

- Jobs não sejam perdidos em restart
- Arquivos persistam até expiração
- Broker mantenha estado de filas

---

### Observações Operacionais

- Alterações em código exigem rebuild (`--build`)
- Alterações apenas no `docker-compose.yml` não exigem rebuild
- Containers são stateless (exceto serviços com volume)

Logs podem ser inspecionados via:

```bash
docker compose logs -f
```

Ou por serviço específico:

```bash
docker compose logs -f worker
```

---

## 🗄️ Banco de Dados & Migrations (Docker)

- **SQLAlchemy 2.0**
- **Alembic**
- `synchronize` não utilizado
- Migrations explícitas e versionadas

As migrations podem ser executadas manualmente dentro do container da API:

```bash
docker compose exec api alembic upgrade head
```

O banco é único, com separação lógica por domínio.

---

## ▶️ Execução Local (Ambiente Containerizado)

Pré-requisitos:

- Docker
- Docker Compose
- Arquivo `.env` configurado corretamente

Subida do ambiente:

```bash
docker compose up --build
```

Parada:

```bash
docker compose down
```

Parada removendo volumes:

```bash
docker compose down -v
```

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
poetry run celery -A src.app.workers.celery_app beat --loglevel=info
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

---

## UPGRADE — Observabilidade e Isolamento de Serviços

[ ] Separar API HTTP do worker Chromium/render
[ ] Criar imagem Docker dedicada para renderização
[ ] Remover dependências desnecessárias entre serviços
[ ] Isolar scheduler/beat em container próprio
[ ] Implementar agente central de auditoria/logs
[ ] Centralizar:
    - errors
    - warnings
    - eventos críticos
    - métricas básicas
    - falhas de jobs
[ ] Adicionar alertas por email para falhas críticas
[ ] Criar sistema de download autorizado de logs
[ ] Adicionar retenção/rotação de logs
[ ] Mapear consumo de memória/CPU por worker
[ ] Adicionar correlation-id/job-id entre serviços
[ ] Avaliar tracing distribuído no futuro
[ ] Reduzir tamanho das imagens Docker por função
[ ] Revisar boundaries entre:
    - API
    - workers
    - scheduler
    - auditoria