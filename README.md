# Doc Flow

## Visão Geral

O **Doc Flow** é um sistema backend para **conversão e processamento assíncrono de documentos**, com foco em:

* Pipelines assíncronas baseadas em mensageria
* Workers isolados do ciclo HTTP
* Notificações em tempo real via WebSockets
* Isolamento por `client_id` anônimo (sem autenticação)
* Controle de recursos e expiração automática de dados

O objetivo é demonstrar **decisões arquiteturais corretas para processamento de documentos em escala**, com separação clara de responsabilidades, idempotência e previsibilidade operacional.

Não é uma plataforma de gestão documental completa.
É um motor de conversão robusto, observável e tecnicamente coerente.

---

# Escopo (congelado)

## Incluído

* Upload de documentos
* Conversão de múltiplos formatos
* Extração básica de conteúdo
* Processamento assíncrono via Celery + RabbitMQ
* Notificações em tempo real via WebSockets (Socket.IO + Redis pub/sub)
* Persistência mínima de estado de jobs (PostgreSQL)
* Armazenamento temporário isolado por cliente
* Limite de 250 MB por `client_id`
* Expiração automática após 24 horas
* Rate limiting: 10 requisições por segundo por IP
* Identificação de cliente via cookie `client_id` (UUID v4 anônimo)

## Explicitamente fora do escopo

* Sistema de usuários / login
* Autenticação / autorização
* Multi-tenant
* Billing
* Workflows complexos
* Versionamento de documentos
* Arquivos muito grandes (>250 MB por cliente)
* Processamento dependente de layout visual complexo

O escopo não deve evoluir além desses limites.

---

# Arquitetura Geral

O sistema segue o modelo de **monólito modular com fronteiras claras**, permitindo futura extração de componentes sem acoplamento excessivo.

```bash
[ Browser / Next.js ]
          |          ↑ WebSocket (Socket.IO)
          |          ↓ Notificações em tempo real
          v
[ Flask API + Socket.IO ]
          |
          | HTTP (upload, status, listagem)
          v
[ PostgreSQL ]  ← estado dos jobs
          |
          v
[ RabbitMQ ] ──► [ Celery Workers ] ──► [ Storage Local ]
                               |
                               v
                           [ Redis ]
                             ↑↓ Pub/Sub (notificações)
```

---

# Componentes

## API — Flask

Responsabilidades:

* Receber uploads
* Criar jobs
* Validar limites
* Orquestrar o fluxo
* Emitir eventos via Socket.IO

Não executa processamento pesado.

---

## Fila — RabbitMQ

* Transporte apenas de metadados
* Nenhum binário trafega pela fila
* Comunicação desacoplada entre API e workers

---

## Workers — Celery

* Executam conversões
* Atualizam status
* Publicam eventos no Redis
* Isolados do ciclo HTTP

---

## Banco de Dados — PostgreSQL

* Persistência do ciclo de vida de jobs
* Auditoria técnica
* Controle de expiração

---

## Cache / PubSub — Redis

* Cache de status
* TTL configurável
* Canal pub/sub para WebSockets

---

## Storage

* Volumes Docker
* Estrutura isolada por cliente
* Diretórios separados para input/output

---

# Identificação e Isolamento de Clientes

## Modelo

* Cada cliente recebe um **UUID v4 anônimo**
* Armazenado em cookie `client_id`
* Criado no primeiro upload
* Duração: 24 horas
* Não é renovado automaticamente

Após expiração ou remoção do cookie:

* Jobs associados são removidos
* Arquivos físicos são deletados
* Cota é liberada

---

## Isolamento físico

Estrutura de diretórios:

```
/storage/input/{client_id}/
/storage/output/{client_id}/
```

---

## Limite de armazenamento

* 250 MB por `client_id`
* Soma de input + output
* Novos uploads são bloqueados quando o limite é atingido

---

# Estratégia de Arquivos

## Regra fundamental

> Arquivos nunca trafegam pela fila.

## Fluxo

1. API recebe upload
2. Arquivo salvo em `/tmp/input/{client_id}`
3. Job persistido no banco
4. Mensagem enviada ao RabbitMQ contendo:

   * `job_id`
   * paths
   * parâmetros
5. Worker processa
6. Output movido para `/storage/output/{client_id}`
7. Status atualizado
8. Evento publicado no Redis
9. Arquivo expira após TTL

---

# Identificação de Jobs

* UUID v4 como chave primária
* Gerado na aplicação

Motivações:

* Evita enumeração
* Facilita correlação de logs
* Compatível com arquitetura distribuída

---

# Modelo de Dados (mínimo)

## DocumentJob

* `id (UUID)`
* `client_id (UUID)`
* `status` (PENDING | PROCESSING | DONE | FAILED)
* `input_filename`
* `input_path`
* `output_format`
* `output_path`
* `error_message`
* `created_at`
* `processed_at`
* `expires_at`

O banco representa apenas o ciclo de vida técnico de jobs.

---

# Notificações em Tempo Real

WebSocket via Socket.IO com Redis pub/sub.

## Fluxo

1. Worker altera status
2. Publica evento no Redis
3. API consome evento
4. Evento emitido para `room(client_id)`

## Eventos

* `job_processing`
* `job_done`
* `job_failed`

Sem polling contínuo.

---

# Estratégia de Expiração

* TTL padrão: 24h
* Campo `expires_at` persistido
* Tarefa periódica (Celery Beat) executa:

  * Limpeza de registros
  * Remoção física de arquivos
  * Liberação de cota

Efemeridade é regra do sistema.

---

# Conversões Suportadas

## 1. Dados tabulares

* CSV ↔ Excel ↔ JSON ↔ Parquet
* Biblioteca: `pandas`

## 2. Texto estruturado

* Markdown ↔ HTML ↔ TXT
* Bibliotecas: `markitdown`, `markdown`

## 3. TXT → PDF

* `ReportLab`, `fpdf`

## 4. PDF → TXT

* `pdfplumber`, `PyPDF2`, `tika`

## 5. Office → formatos de visão

* DOCX / PPTX → PDF / Markdown
* `docling`, `python-docx`, `markitdown`

Conversões dependentes de layout complexo não são objetivo.

---

# Stack Tecnológica

## Backend

* Python 3.11+
* Flask
* SQLAlchemy 2.0
* Alembic
* Celery
* RabbitMQ
* Redis
* PostgreSQL

## Infra

* Docker
* Docker Compose

## Qualidade

* pytest
* logging estruturado

---

# Frontend

Interface operacional mínima.

## Stack

* Next.js
* Tailwind CSS
* shadcn/ui

## Funções

* Upload
* Listagem de jobs
* Visualização de status
* Download

Sem lógica de negócio relevante.

---

# Princípios Arquiteturais

* Escopo controlado
* Mensageria correta
* Separação de responsabilidades
* Idempotência
* Observabilidade
* Arquitetura evolutiva sem overengineering
* Efemeridade por design

---

# Comandos para execução

```bash
poetry run start-api
```

```bash
poetry run start-worker
```

```bash
poetry run celery -A src.workers.celery_app beat --loglevel=info
```

---

# Observação Final

Este projeto não é um CRUD nem um protótipo superficial.

Ele demonstra como sistemas reais de processamento de documentos são estruturados para:

* Escalar
* Isolar responsabilidades
* Controlar recursos
* Evitar acoplamento indevido
* Manter previsibilidade operacional

O foco é engenharia responsável, não volume de funcionalidades.
