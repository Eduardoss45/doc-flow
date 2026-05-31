# TODO — Hardening Progressivo do Pipeline Markdown → PDF

## Estado atual

Pipeline atual:

```txt
Markdown
→ markdown-it-py
→ sanitize HTML
→ process assets
→ render HTML
→ Playwright/Chromium
→ PDF
```

Objetivo atual:
melhorar segurança e previsibilidade operacional sem destruir a flexibilidade do sistema.

---

# PRIORIDADE 1 — Assets gigantes

## Objetivo

Evitar:

* explosão de RAM;
* downloads abusivos;
* degradação do worker;
* imagens enormes carregadas integralmente em memória.

---

## 1.1 — Trocar download simples por streaming

### Atual

```python
requests.get(url).content
```

### Objetivo

```txt
GET stream=True
→ leitura em chunks
→ aborta ao exceder limite
```

---

## 1.2 — Adicionar limite hard de download

Criar:

```python
MAX_IMAGE_SIZE = 5 * 1024 * 1024
```

Abortar imediatamente se exceder.

---

## 1.3 — Salvar em arquivo temporário

Objetivo:
evitar manter imagens grandes em memória.

---

## 1.4 — Validar MIME-Type

Permitir apenas:

* image/png
* image/jpeg
* image/webp
* image/gif

---

## 1.5 — Validar Content-Length

Se existir header:

```txt
Content-Length
```

E exceder limite:
abortar antes do download.

---

## 1.6 — Substituir src remoto por local

Fluxo:

```txt
imagem remota
→ download backend
→ salva temporário
→ src=file://local
```

---

# PRIORIDADE 2 — Render infinito

## Objetivo

Evitar Chromium preso em render.

---

## 2.1 — Adicionar timeout hard

Aplicar:

```python
page.set_default_timeout(30000)
```

---

## 2.2 — Timeout no PDF

Usar:

```python
asyncio.wait_for(...)
```

ou equivalente sync.

---

## 2.3 — Garantir cleanup

Sempre:

```python
browser.close()
```

Mesmo em exceção.

Usar:

```python
try/finally
```

---

## 2.4 — Bloquear JavaScript

Garantir:

```python
java_script_enabled=False
```

---

# PRIORIDADE 3 — Consumo de memória

## Objetivo

Evitar worker morrendo sob carga.

---

## 3.1 — Adicionar limites Docker

docker-compose:

```yaml
mem_limit: 1g
cpus: 1.0
```

---

## 3.2 — Worker dedicado Chromium

Separar:

```txt
worker-markdown
```

---

## 3.3 — Queue dedicada

Criar:

```txt
markdown_pdf_queue
```

---

## 3.4 — Limitar concorrência

Objetivo:
evitar múltiplos Chromium simultâneos.

---

# PRIORIDADE 4 — HTML explosivo

## Objetivo

Evitar HTML monstruoso destruindo render.

---

## 4.1 — Limite tamanho markdown

Exemplo:

```python
MAX_MARKDOWN_SIZE = 2 * 1024 * 1024
```

---

## 4.2 — Limite de linhas

Exemplo:

```python
MAX_LINES = 20000
```

---

## 4.3 — Limite de imagens

Exemplo:

```python
MAX_IMAGES = 20
```

---

## 4.4 — Limite de tabelas

Evitar:

* tabelas absurdas;
* milhares de células.

---

## 4.5 — Limite tamanho HTML final

Abortar HTML excessivo antes do Chromium.

---

# PRIORIDADE 5 — Refinamento requests externos

## Objetivo

Melhorar controle sem destruir flexibilidade.

---

## 5.1 — Melhorar whitelist

Atual:
hostname exato.

Depois:

* subdomínios;
* CDN segura;
* regras mais refinadas.

---

## 5.2 — Adicionar cache local

Evitar baixar asset repetido.

---

## 5.3 — Adicionar retry controlado

Evitar:

* falhas temporárias;
* timeout simples.

---

## 5.4 — Validar extensões

Aceitar apenas:

* .png
* .jpg
* .jpeg
* .webp
* .gif

---

# PRIORIDADE 6 — Observabilidade

## Objetivo

Entender comportamento real do pipeline.

---

## 6.1 — Logging estruturado

Registrar:

* tempo render;
* tamanho markdown;
* quantidade imagens;
* tamanho assets;
* tempo download;
* tempo Chromium.

---

## 6.2 — Métricas

Medir:

* falhas;
* timeout;
* memória;
* duração média;
* throughput.

---

# PRIORIDADE 7 — Evolução futura

Somente após validar uso real.

---

## Possíveis evoluções

* templates premium;
* preview em tempo real;
* TOC automático;
* header/footer;
* dark mode;
* cache render;
* render distribuído;
* pool Chromium.

---

# Regra principal do projeto

Não implementar múltiplos hardenings simultaneamente.

Fluxo ideal:

1 problema
→ implementar
→ testar
→ medir
→ seguir para próximo

```
```
