# Ordem de Implementação — Chromium/Playwright no Doc Flow

A ideia aqui é:

- encaixar Chromium no design atual;
- evitar acoplamento;
- manter isolamento;
- preparar para escala futura;
- evitar quebrar o pipeline existente.

---

# FASE 1 — Definir o Pipeline de Conversão

## Objetivo

Padronizar como o Markdown vira PDF.

---

# 1.1 — Fluxo oficial

Definir o pipeline como:

```txt id="g1mz9f"
Markdown
→ sanitize
→ parse markdown
→ render HTML
→ render Chromium
→ PDF
```

---

# 1.2 — Decidir parser Markdown

## Recomendação

- [markdown-it-py](https://markdown-it-py.readthedocs.io/en/latest/?utm_source=chatgpt.com)

Porque:

- GitHub flavored markdown;
- extensível;
- moderno;
- estável.

---

# 1.3 — Syntax Highlight

## Recomendação

- [Pygments](https://pygments.org/?utm_source=chatgpt.com)

Objetivo:

- code blocks;
- temas;
- export técnico bonito.

---

# FASE 2 — Criar o Conversor MD → PDF

## Objetivo

Adicionar conversão como first-class citizen do Doc Flow.

---

# 2.1 — Adicionar tipo de conversão

Exemplo:

```python id="w94r0g"
class ConversionType(str, Enum):
    MARKDOWN_TO_PDF = "md_to_pdf"
```

---

# 2.2 — Criar conversor dedicado

Estrutura:

```txt id="t24b3v"
src/app/converters/markdown_to_pdf/
```

---

# 2.3 — Estrutura recomendada

```txt id="jlwm1n"
markdown_to_pdf/
├── converter.py
├── renderer.py
├── templates/
├── assets/
├── styles/
└── sanitize.py
```

---

# 2.4 — Interface do conversor

```python id="fh84e4"
class MarkdownToPdfConverter:
    def convert(
        self,
        input_path: str,
        output_path: str
    ) -> None:
        ...
```

---

# FASE 3 — Implementar Parsing Markdown

## Objetivo

Gerar HTML consistente.

---

# 3.1 — Pipeline interno

```python id="9zkbpd"
markdown
→ markdown-it-py
→ HTML
→ Jinja template
```

---

# 3.2 — Template base

Criar:

```txt id="go0dzu"
templates/base.html
```

Com:

- typography;
- spacing;
- print styles;
- code highlighting.

---

# 3.3 — CSS Print

Muito importante.

Criar:

```txt id="f5e8s2"
styles/github.css
styles/dark.css
styles/technical.css
```

---

# FASE 4 — Implementar Chromium Rendering

## Objetivo

Gerar PDF real.

---

# 4.1 — Instalar Playwright

[Playwright Python Docs](https://playwright.dev/python/?utm_source=chatgpt.com)

---

# 4.2 — Instalar Chromium no container

Dockerfile:

```dockerfile id="ntd3fc"
RUN playwright install chromium
```

---

# 4.3 — Criar renderer isolado

Exemplo:

```python id="zv4m1h"
async def render_pdf(
    html: str,
    output_path: str
):
    ...
```

---

# 4.4 — Fluxo Playwright

```python id="98m4qo"
browser = await playwright.chromium.launch()

page = await browser.new_page()

await page.set_content(html)

await page.pdf(
    path=output_path,
    format="A4",
    print_background=True
)
```

---

# 4.5 — Adicionar print CSS

Muito importante:

```css id="9gw9tx"
@media print {
    ...
}
```

---

# FASE 5 — Hardening

## Objetivo

Evitar que Chromium destrua o worker.

---

# 5.1 — Timeout obrigatório

Exemplo:

```python id="0o3pzh"
asyncio.wait_for(render(), timeout=60)
```

---

# 5.2 — Limite de tamanho

Adicionar:

- tamanho máximo;
- limite de imagens;
- limite de linhas;
- limite de páginas.

---

# 5.3 — Sanitização Markdown

## Remover:

- scripts;
- embeds;
- HTML perigoso.

---

# 5.4 — Isolamento Chromium

Idealmente:

- browser por task;
- contexto isolado;
- cleanup obrigatório.

---

# 5.5 — Cleanup

Sempre:

```python id="w19bq0"
await browser.close()
```

Mesmo em exceção.

---

# FASE 6 — Integração com Worker Atual

## Objetivo

Acoplar sem quebrar arquitetura.

---

# 6.1 — Adicionar no registry

```python id="2ftjlwm"
CONVERTERS = {
    ("md", "pdf"): MarkdownToPdfConverter(),
}
```

---

# 6.2 — Padronizar erros

Separar:

- input inválido;
- timeout;
- render failure;
- browser crash.

---

# 6.3 — Logging estruturado

Exemplo:

```json id="jlwmo0"
{
  "conversion": "md_to_pdf",
  "duration_ms": 5321,
  "status": "DONE"
}
```

---

# FASE 7 — Docker & Infra

## Objetivo

Garantir previsibilidade operacional.

---

# 7.1 — Worker dedicado

Recomendado:

```txt id="nlm2yi"
worker-markdown
```

Porque Chromium:

- pesa;
- usa RAM;
- tem comportamento diferente.

---

# 7.2 — Queue dedicada

```txt id="e3yggn"
markdown_pdf_queue
```

---

# 7.3 — Resource limits

Docker compose:

```yaml id="qtctij"
mem_limit: 1g
cpus: 1.0
```

---

# FASE 8 — Frontend

## Objetivo

Expor a feature corretamente.

---

# 8.1 — Página dedicada

```txt id="nq2cjlwm"
/markdown-to-pdf
```

---

# 8.2 — Upload simples

Fluxo:

```txt id="ykjlwm"
upload
→ processing
→ download
```

---

# 8.3 — Templates futuros

Depois:

- GitHub style;
- technical;
- dark;
- minimal.

---

# FASE 9 — Observabilidade

## Objetivo

Entender custo real do Chromium.

---

# 9.1 — Métricas

Medir:

- tempo render;
- RAM;
- falhas;
- páginas;
- tamanho.

---

# 9.2 — Queue monitoring

Especialmente:

- backlog;
- saturation;
- throughput.

---

# FASE 10 — Evolução futura

Somente depois de validar uso.

---

# Possíveis melhorias

## Preview em tempo real

```txt id="i0v3uw"
Markdown
→ HTML preview
```

---

## Multi-template

- GitHub
- Obsidian
- Documentation
- Academic

---

## TOC automático

---

## Header/Footer

---

## Dark mode export

---

# Ordem REAL resumida

## Primeiro

1. markdown-it-py
2. template HTML
3. Playwright
4. render PDF

---

## Depois

5. sanitização
6. timeout
7. logging
8. queue dedicada

---

## Depois

9. observabilidade
10. templates
11. preview
12. premium features
