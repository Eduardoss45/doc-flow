# TODO – Doc Flow

Pendências e ideias após a fase de infraestrutura (imagens especializadas, Poetry groups, secrets, healthcheck, Gunicorn, non-root, docs e licença source-available).

Este arquivo **não** inclui CQRS nem mudanças arquiteturais grandes desse tipo.

---

## Fase A – Higiene e endurecimento (curto prazo)

### Repo e código

- [ ] Adicionar `celerybeat-schedule*` (e variantes `.dat`, `.dir`, `.bak`, `-shm`, `-wal`) ao `.gitignore`
- [ ] Remover do versionamento os arquivos de schedule do Celery já commitados em `apps/api/`
- [ ] Corrigir ou remover `apps/api/src/app/entrypoints/beat.py` (import inválido: `from workers.celery_app import celery`)
- [ ] Limpar imports fantasmas / não usados (ruff ou equivalente)
- [ ] Remover `print` de debug no worker (ex.: mensagens residuais de desenvolvimento)
- [ ] Unificar documentação de env: raiz `.env.example` vs `apps/api/.env.example` (um canônico + nota no README)

### Compose e runtime

- [ ] Worker e celery: `depends_on` do backend com `condition: service_healthy` (como o serviço `web`)
- [ ] Definir limites de recurso no worker (`mem_limit`, `cpus`) no `docker-compose.yml`
- [ ] Revisar intervalo do cleanup do Beat (hoje a cada 1 min; avaliar 5–15 min em operação real)
- [ ] Tratar Poetry `--no-root` / warnings de entry points (instalar o pacote ou CMD sem `poetry run` onde fizer sentido)

### API e Socket.IO

- [ ] Health “ready” opcional (`/health/ready`) checando DB e/ou Redis, mantendo `/health` leve para o Compose
- [ ] Preparar `message_queue` Redis no Socket.IO se no futuro houver mais de 1 worker Gunicorn
- [ ] CORS: suporte explícito a múltiplas origens em `ALLOWED_ORIGINS` (parse por vírgula)
- [ ] Revisar default de `FLASK_DEBUG` / `FLASK_ENV` no `config.py` (evitar default confuso em produção)

### Testes

- [ ] Teste mínimo de health
- [ ] Teste mínimo de um converter (unitário)
- [ ] Teste de fluxo de upload/enqueue (mock do Celery)

---

## Fase B – Staging / deploy real

### Rede e configuração

- [ ] Não publicar Postgres, RabbitMQ e Redis na internet (apenas rede interna)
- [ ] HTTPS + cookie `Secure` no `client_id`
- [ ] `NEXT_PUBLIC_API_URL` (e correlatos) por ambiente no build do frontend — não fixar `localhost` em produção
- [ ] Dockerfile do `web`: config completa de produção (standalone/non-root se aplicável)

### Dados e schema

- [ ] Introduzir **Alembic** (migrations) no lugar de só `create_all` no boot
- [ ] Storage de arquivos em object storage (S3/R2/compatível) em vez de volume local apenas

### Observabilidade

- [ ] Logging estruturado (substituir `print`s)
- [ ] Error tracking (ex.: Sentry)
- [ ] Métricas básicas (fila, tempo de conversão, erros por tipo)

### Segurança operacional

- [ ] Rotacionar senhas antigas que possam existir no histórico do Git
- [ ] Rate limit mais específico em criação de `client_id` e upload
- [ ] Revisar exposição do management UI do RabbitMQ

---

## Fase C – Produto (SaaS)

- [ ] Decidir modelo: continuar anônimo com quotas **ou** contas reais (magic link / OAuth)
- [ ] Se contas: sessão/token server-side ou JWT; abandonar UUID “adivinhavel” como único controle
- [ ] API keys para uso programático (opcional)
- [ ] Planos / limites por conta
- [ ] Dashboard de histórico estável
- [ ] Termos de uso, privacidade e política de retenção (alinhar ao cleanup existente)
- [ ] Landing / narrativa de produto (além das páginas de converter)

---

## Fase D – Escala (somente com uso real medido)

- [ ] Mais workers Gunicorn + `message_queue` no Socket.IO
- [ ] Fila ou worker dedicado para jobs pesados (Markdown→PDF / LibreOffice)
- [ ] CDN ou URLs assinadas para download
- [ ] Alertas de fila e latência

---

## Fora de escopo (por enquanto)

- CQRS formal (dois modelos de dados, buses, projeções generalizadas)
- Microserviços / split de repositórios
- Kubernetes (enquanto Docker Compose + um host/staging bastar)

---

## Ordem sugerida na volta ao código

1. Gitignore + limpeza dos schedules do Celery  
2. Corrigir `beat.py`  
3. Compose: `service_healthy` + limites do worker  
4. Env canônico + pequenos ajustes de API  
5. Testes mínimos  
6. Só então staging (HTTPS, portas, object storage, Alembic)
