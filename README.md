# Document Processor

## Visão Geral

Este projeto é um **sistema backend de conversão e processamento de documentos**, com foco em **pipelines assíncronos**, **workers**, **filas** e **manipulação confiável de arquivos** — um cenário comum em empresas de médio e grande porte nos setores financeiro, jurídico, saúde e dados.

O objetivo **não** é construir uma plataforma completa, mas sim demonstrar **decisões arquiteturais corretas**, **isolamento de responsabilidades** e **processamento de documentos em escala**, mantendo o escopo estritamente controlado.

---

## Escopo (congelado)

### Incluído

- Upload de documentos
- Conversão de documentos
- Processamento básico (ex: extração de texto)
- Execução assíncrona via fila + workers
- Persistência de estado dos jobs
- Retenção temporária de arquivos

### Explicitamente fora do escopo

- Sistema de usuários
- Autenticação / autorização
- Multi‑tenant
- Billing
- Workflows complexos
- Versionamento de documentos

O projeto **não deve evoluir além desses limites**.

---

## Arquitetura Geral

O sistema segue um modelo **monólito modular**, com fronteiras claras para uma eventual extração futura em microserviços, caso necessário.

### Componentes

- **API (Flask)**
  - Recebe uploads
  - Cria jobs
  - Orquestra o fluxo

- **Fila (RabbitMQ)**
  - Transporte apenas de metadados
  - Nenhum arquivo binário trafega pela fila

- **Workers (Celery)**
  - Executam conversões e processamentos
  - Isolados do ciclo HTTP

- **Banco de Dados (PostgreSQL)**
  - Persistência de estado
  - Auditoria técnica

- **Cache (Redis)**
  - Cache de status/resultados
  - TTL configurável (default: 1h)

- **Storage Local (volumes Docker)**
  - Armazenamento temporário e definitivo de arquivos

---

## Diagrama Base (referência)

```bash
[ Client (Next.js) ]
          |
          v
[ Flask API ]
          |
          v
[ PostgreSQL ]
          |
          v
[ RabbitMQ ] ---> [ Celery Workers ] ---> [ Storage ]
                               |
                               v
                           [ Redis Cache ]
```

> Este diagrama é **referencial** e serve apenas para orientar decisões futuras sem comprometer o escopo atual.

---

## Estratégia de Arquivos

### Regra fundamental

> **Arquivos nunca trafegam pela fila.**

### Fluxo

1. API recebe o upload
2. Arquivo salvo em diretório temporário (`/tmp/input`)
3. Job persistido no banco
4. Mensagem enviada à fila contendo apenas:
   - `job_id`
   - paths
   - parâmetros de conversão

5. Worker processa o arquivo
6. Resultado movido para diretório definitivo (`/storage/output`)
7. Cache de resultado/status aplicado
8. Arquivos expiram após TTL configurado

---

## Identificação de Jobs

- Todos os jobs utilizam **UUID v4** como chave primária
- UUID é gerado na aplicação

### Motivos

- Evita enumeração de recursos
- Compatível com sistemas distribuídos
- Facilita correlação de logs e eventos

---

## Modelo de Dados (mínimo)

### DocumentJob

- `id (UUID)`
- `status` (PENDING | PROCESSING | DONE | FAILED)
- `input_filename`
- `input_path`
- `output_format`
- `output_path`
- `error_message`
- `created_at`
- `processed_at`
- `expires_at`

O banco **não representa usuários**, apenas o ciclo de vida de jobs.

---

## Frontend

O frontend é **secundário** e serve apenas como interface operacional.

### Stack

- Next.js
- Tailwind CSS
- shadcn/ui

### Funcionalidades

- Upload de arquivos
- Listagem de jobs
- Visualização de status
- Download de resultado

Sem SSR complexo, sem API Routes e sem lógica de negócio.

---

## Conversões Suportadas (foco inicial)

As conversões foram escolhidas com base em **estabilidade**, **previsibilidade** e **aderência ao ecossistema Python**.

### 1. Dados tabulares e estruturados

- CSV ↔ Excel ↔ JSON ↔ Parquet
- Biblioteca: `pandas`

### 2. Texto e documentos estruturados

- Markdown ↔ HTML ↔ TXT
- Bibliotecas: `markitdown`, `markdown`

### 3. Texto puro para PDF

- TXT → PDF
- Bibliotecas: `ReportLab`, `fpdf`

### 4. Extração de texto de PDFs

- PDF → TXT
- Bibliotecas: `pdfplumber`, `PyPDF2`, `tika`

### 5. Office para formatos de visão

- DOCX / PPTX → PDF / Markdown
- Bibliotecas: `docling`, `python-docx`, `markitdown`

Conversões que dependem fortemente de layout complexo **não são objetivo do projeto**.

---

## Stack Tecnológica

### Backend

- Python 3.11+
- Flask
- SQLAlchemy 2.0
- Alembic
- Celery
- RabbitMQ
- Redis
- PostgreSQL

### Infra

- Docker
- Docker Compose

### Qualidade

- pytest
- logging estruturado

---

## Princípios do Projeto

- Escopo controlado
- Mensageria correta
- Separação de responsabilidades
- Idempotência
- Facilidade de debug
- Arquitetura evolutiva sem overengineering

---

## Observação Final

Este projeto **não é um CRUD**, nem um demo superficial.

Ele existe para demonstrar **como sistemas reais de processamento de documentos são desenhados**, mantidos e evoluídos de forma responsável.
