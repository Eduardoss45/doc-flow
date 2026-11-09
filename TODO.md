# TODO – Doc Flow

Pendências e ideias após a fase de infraestrutura (imagens especializadas, Poetry groups, secrets, healthcheck, Gunicorn, non-root, docs e licença source-available).

Este arquivo **não** inclui CQRS nem mudanças arquiteturais grandes desse tipo.

---

## Fase A – Higiene e endurecimento

**Concluída.** Incluiu gitignore/schedules do Celery, `beat.py`, Compose (`service_healthy`, limites do worker), env canônico, defaults FLASK, CORS multi-origem, cleanup do Beat, `/health/ready`, testes mínimos, imports não usados, prints de debug e install Poetry com pacote root.

O item de `message_queue` no Socket.IO ficou na **Fase D** (só faz sentido com mais de 1 worker Gunicorn).

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

- [ ] Logging estruturado (substituir `print`s restantes de boot/conexão)
- [ ] Error tracking (ex.: Sentry)
- [ ] Métricas básicas (fila, tempo de conversão, erros por tipo)

### Segurança operacional

- [ ] Rotacionar senhas antigas que possam existir no histórico do Git
- [ ] Rate limit mais específico em criação de `client_id` e upload
- [ ] Revisar exposição do management UI do RabbitMQ

---

## Fase C – Produto (SaaS)

- [ ] Decidir modelo: continuar anônimo com quotas **ou** contas reais (magic link / OAuth)
- [ ] Se contas: sessão/token server-side ou JWT; abandonar UUID “adivinhável” como único controle
- [ ] API keys para uso programático (opcional)
- [ ] Planos / limites por conta
- [ ] Dashboard de histórico estável
- [ ] Termos de uso, privacidade e política de retenção (alinhar ao cleanup existente)
- [ ] Landing / narrativa de produto (além das páginas de converter)

---

## Fase D – Escala (somente com uso real medido)

- [ ] Mais workers Gunicorn + `message_queue` Redis no Socket.IO
- [ ] Fila ou worker dedicado para jobs pesados (Markdown→PDF / LibreOffice)
- [ ] CDN ou URLs assinadas para download
- [ ] Alertas de fila e latência

---

## Fora de escopo (por enquanto)

- CQRS formal (dois modelos de dados, buses, projeções generalizadas)
- Microserviços / split de repositórios
- Kubernetes (enquanto Docker Compose + um host/staging bastar)

---

## Ordem sugerida

1. Staging: portas internas, HTTPS, `NEXT_PUBLIC_*` por ambiente  
2. Alembic + object storage  
3. Observabilidade (logging, Sentry, métricas básicas)  
4. Segurança operacional (rate limit, RabbitMQ UI, rotação de segredos no histórico)  
