# Pipeline de Desenvolvimento — Doc Flow SaaS

A ideia aqui é:

* evitar overengineering;
* evitar retrabalho;
* manter entrega incremental;
* colocar em produção cedo;
* validar antes de escalar.

A ordem abaixo considera:

* o Doc Flow já funcional arquiteturalmente;
* backend já estabilizado;
* workers/mensageria já existentes;
* foco comercial em:

  * PDF → TXT
  * Markdown → PDF.

---

# FASE 0 — Congelamento Arquitetural

## Objetivo

Parar de mexer na fundação.

Você já tem:

* Flask;
* Celery;
* RabbitMQ;
* Redis;
* PostgreSQL;
* Docker;
* WebSocket;
* pipeline assíncrono.

NÃO:

* migrar stack;
* separar microserviços;
* adicionar Kubernetes;
* reinventar arquitetura.

---

# FASE 1 — Refinamento do Domínio de Conversão

## Objetivo

Transformar o projeto técnico em engine utilizável.

---

## 1.1 — Normalizar contratos de conversão

Criar interface única:

```python
class Converter:
    input_formats: list[str]
    output_formats: list[str]

    async def convert(
        self,
        input_path: str,
        output_path: str
    ) -> ConversionResult:
        ...
```

---

## 1.2 — Criar registry central

Exemplo:

```python
CONVERTERS = {
    ("pdf", "txt"): PdfToTextConverter(),
    ("md", "pdf"): MarkdownToPdfConverter(),
}
```

Isso evita:

* if/else espalhado;
* acoplamento;
* roteamento manual.

---

## 1.3 — Implementar Markdown → PDF

## Pipeline recomendado

```txt id="1r7xqh"
Markdown
→ HTML
→ Template
→ Chromium
→ PDF
```

### Stack recomendada

* markdown-it-py
* pygments
* jinja2
* playwright

---

## 1.4 — Padronizar output

Estrutura:

```json
{
  "job_id": "...",
  "status": "DONE",
  "duration_ms": 1234,
  "input_size": 12345,
  "output_size": 56789,
  "mime_type": "application/pdf"
}
```

---

# FASE 2 — Hardenização do Pipeline

## Objetivo

Evitar que processamento real destrua o sistema.

---

## 2.1 — Timeouts obrigatórios

Por conversão:

| Conversão      | Timeout |
| -------------- | ------- |
| PDF → TXT      | 30s     |
| Markdown → PDF | 60s     |

---

## 2.2 — Limites de memória

Especialmente Chromium.

Adicionar:

* limite de páginas;
* limite de tamanho;
* limite de imagens.

---

## 2.3 — Retry + DLQ

Separar:

* falha temporária;
* falha permanente.

Exemplo:

* timeout → retry;
* PDF inválido → fail direto.

---

## 2.4 — Sanitização

Muito importante.

### Markdown

* remover HTML perigoso;
* limitar embeds;
* bloquear scripts.

### PDF

* validar mime;
* validar extensão;
* validar magic bytes.

---

## 2.5 — Logging estruturado

Adicionar:

```json
{
  "job_id": "...",
  "conversion": "md_to_pdf",
  "duration_ms": 1234,
  "status": "DONE"
}
```

---

# FASE 3 — Frontend de Produto

## Objetivo

Parar de parecer ferramenta interna.

---

# 3.1 — Landing page mínima

Estrutura:

```txt id="9kv7mb"
Hero
↓
Upload
↓
Conversão
↓
Download
```

---

# 3.2 — Páginas individuais SEO

Criar:

```txt id="xfr2rz"
/pdf-to-text
/markdown-to-pdf
```

---

# 3.3 — UX de processamento

Estados:

* uploading;
* queued;
* processing;
* completed;
* failed.

Você já possui backend para isso.

---

# 3.4 — Download efêmero

Links temporários:

* expiram;
* assinados;
* sem acesso direto ao storage.

---

# FASE 4 — Deploy Inicial

## Objetivo

Colocar online rapidamente.

---

# 4.1 — Infra mínima

## Sugestão

### Backend

* VPS Linux simples

### Storage

* local inicialmente

### Reverse proxy

* Nginx

---

# 4.2 — HTTPS

Obrigatório.

Use:

* Let's Encrypt
* Caddy ou Nginx.

---

# 4.3 — Ambiente separado

Separar:

* dev;
* staging;
* prod.

Mesmo simples.

---

# 4.4 — CI/CD mínimo

Pipeline:

```txt id="0o0n3n"
push
→ tests
→ build
→ deploy
```

---

# FASE 5 — Observabilidade

## Objetivo

Entender uso real.

---

# 5.1 — Analytics de produto

Rastrear:

* conversão mais usada;
* falhas;
* tamanho médio;
* tempo médio;
* abandono.

---

# 5.2 — Métricas técnicas

Adicionar:

* queue depth;
* worker throughput;
* memory usage;
* conversion duration.

---

# 5.3 — Error tracking

Exemplo:

* Sentry.

---

# FASE 6 — SEO & Distribuição

## Objetivo

Trazer usuários.

---

# 6.1 — Conteúdo SEO

Criar:

* páginas indexáveis;
* FAQ;
* exemplos;
* keywords.

---

# 6.2 — Performance Web

Melhorar:

* Core Web Vitals;
* TTFB;
* lazy loading.

---

# 6.3 — Open Graph

Importante para compartilhamento.

---

# FASE 7 — Monetização

## Objetivo

Validar receita.

---

# 7.1 — Limites gratuitos

Exemplo:

* 10 conversões/dia;
* 10MB;
* fila comum.

---

# 7.2 — Premium

Adicionar:

* batch;
* prioridade;
* API;
* histórico;
* arquivos maiores.

---

# 7.3 — API pública

Endpoints:

```http id="kqixmb"
POST /api/v1/convert/pdf-to-text
POST /api/v1/convert/markdown-to-pdf
```

---

# FASE 8 — Evolução Inteligente

Somente após tráfego real.

---

# 8.1 — Storage externo

Migrar:

```txt id="u85gko"
local
→ S3
```

---

# 8.2 — Workers especializados

Separar:

* markdown worker;
* pdf worker.

---

# 8.3 — OCR

Somente se:

* demanda real;
* uso real.

---

# 8.4 — AI Pipelines

Aqui seu projeto pode crescer muito.

Exemplo:

```txt id="zy3qj7"
PDF
→ extraction
→ cleaning
→ chunking
→ embeddings-ready JSON
```

---

# Ordem REALISTA resumida

## AGORA

1. Registry de conversores
2. Markdown → PDF
3. Hardening
4. Frontend minimalista
5. Deploy
6. SEO
7. Analytics

---

## DEPOIS

8. Retry/DLQ
9. Observabilidade
10. API pública
11. Monetização

---

## MUITO depois

12. Scaling avançado
13. OCR
14. Pipelines IA
15. Workers especializados