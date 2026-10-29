# 📌 Doc Flow – Motor Assíncrono de Conversão de Documentos

> **Status:** em desenvolvimento. Não há instância pública nem acesso aberto ao serviço.

O **Doc Flow** é um sistema SaaS de **processamento e conversão assíncrona de documentos**, estruturado como um backend orientado a mensageria, com comunicação desacoplada entre API e workers, processamento distribuído e notificações em tempo real via WebSocket.

O projeto mantém seu objetivo original de fornecer um motor técnico de conversão previsível e observável, agora evoluído com uma camada SaaS e recursos de renderização avançada.

O foco do projeto é demonstrar:

* Separação rigorosa de responsabilidades
* Processamento assíncrono
* Isolamento por cliente sem autenticação
* Controle explícito de recursos
* Efemeridade como regra arquitetural
* Pipeline seguro de conversão
* Preparação da infraestrutura para uma futura operação em produção

O sistema não é uma plataforma de gestão documental.

É um **motor SaaS de conversão de documentos com processamento assíncrono, isolamento de recursos e execução controlada**.

---

# 🔄 Pipelines de Conversão

Os tipos de conversão atualmente registrados no worker são:

* CSV → JSON
* CSV → XLSX
* XLSX → CSV
* TXT → PDF
* PDF → TXT
* DOCX → PDF
* DOCX → Markdown
* Markdown → PDF

## Markdown → PDF

O pipeline utiliza **Chromium como engine de renderização**, com uma etapa intermediária baseada em HTML para melhorar a fidelidade visual do documento gerado.

Fluxo:

```text
Markdown
   │
   ▼
Conversão para HTML
   │
   ▼
Renderização Chromium
   │
   ▼
PDF final
```

Esse pipeline oferece:

* Suporte a CSS moderno
* Melhor controle de layout
* Renderização baseada em navegador
* Maior controle sobre a apresentação visual dos documentos

---

# 🔐 Proteções do Pipeline Chromium

A renderização com Chromium exige mais recursos que conversões simples. Por isso, o pipeline inclui medidas de isolamento e controle para reduzir o risco de impacto no restante da aplicação.

As proteções implementadas incluem:

* Execução isolada do processo de conversão
* Controle do tempo de execução
* Limites de tamanho e complexidade para entradas
* Validação e sanitização de conteúdo
* Restrições para carregamento de recursos externos
* Separação entre a API e o processamento mais pesado

O objetivo é tornar a execução de tarefas de maior custo computacional mais previsível.

---

# 🌐 Frontend

O frontend utiliza Next.js e possui páginas de conversão com estrutura voltada à indexação.

O frontend está preparado para SEO e, no futuro, monetização — sem operação pública no momento.

---

# 🐳 Arquitetura de containers

O projeto utiliza um **monólito modular com imagens Docker especializadas por processo**, definidas por targets no Dockerfile da API.

| Target / serviço  | Função |
| ----------------- | ------ |
| `api` / `backend` | Requisições HTTP, WebSocket e enfileiramento de jobs; executado com Gunicorn e eventlet |
| `worker`          | Processamento das conversões, incluindo LibreOffice e Chromium/Playwright |
| `beat` / `celery` | Agendamento de tarefas periódicas e execução de rotinas de cleanup |

A infraestrutura local também utiliza PostgreSQL para persistência, RabbitMQ para mensageria e Redis para funcionalidades auxiliares.

Características da arquitetura:

* Dependências Python separadas por grupos Poetry (`main`, `api` e `worker`)
* Containers da aplicação executados com o usuário não-root `appuser`
* API desacoplada dos conversores: os jobs são enfileirados por nome de tarefa (`send_task`)
* Configurações e credenciais fornecidas por variáveis de ambiente via `.env`, usando `.env.example` como referência
* Healthcheck HTTP da API em `GET /health`

---

# ▶️ Ambiente local

Pré-requisitos: Docker e Docker Compose.

Na raiz do repositório, execute:

```bash
cp .env.example .env
# ajuste as variáveis, especialmente POSTGRES_PASSWORD e as credenciais de serviços
docker compose up -d --build
```

Endereços locais:

* Frontend: http://localhost:3000
* Healthcheck da API: http://localhost:4000/health

Essas instruções são destinadas ao ambiente local de desenvolvimento. Não representam uma instância pública do serviço.

---

# 🚀 Deploy em produção

A base de runtime está preparada com imagens especializadas por processo, configuração por variáveis de ambiente, healthcheck, Gunicorn e execução dos containers da aplicação sem privilégios de root.

**O serviço ainda não foi publicado.** Antes de uma operação real, ainda será necessário configurar a hospedagem, os secrets do provedor, HTTPS e monitoramento, além de validar o comportamento no ambiente de destino.
