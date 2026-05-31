# Teste Completo do Parser Markdown

Este documento existe para validar:

- Parsing Markdown
- Sanitização HTML
- Download de assets
- Renderização Chromium
- Conversão PDF

---

## Imagem válida (Unsplash)

![Montanhas](https://images.unsplash.com/photo-1506744038136-46273834b3fb)

---

## Imagem válida (GitHub Raw)

![GitHub Raw](https://raw.githubusercontent.com/github/explore/main/topics/python/python.png)

---

## Imagem válida (JSDelivr)

![JSDelivr](https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg)

---

## Imagem inválida (domínio não permitido)

Esta imagem deve ser removida pelo pipeline.

![Imagem inválida](https://example.com/image.png)

---

## Imagem inexistente

Esta imagem deve falhar no download.

![404](https://images.unsplash.com/arquivo-inexistente.jpg)

---

## Links

- https://github.com
- https://google.com
- https://openai.com

[Link Markdown](https://github.com)

---

## Lista Simples

- Item 1
- Item 2
- Item 3

---

## Lista Aninhada

- Backend
  - Python
  - Celery
  - Redis

- Frontend
  - React
  - Next.js

---

## Checklist

- [x] Parser
- [x] Sanitização
- [ ] Cache
- [ ] Observabilidade

---

## Citação

> Este é um bloco de citação.
>
> Deve ser renderizado corretamente.

---

## Tabela Simples

| Nome     | Tecnologia |
| -------- | ---------- |
| API      | FastAPI    |
| Worker   | Celery     |
| Frontend | Next.js    |

---

## Tabela Grande

| ID  | Nome  | Status | Tempo |
| --- | ----- | ------ | ----- |
| 1   | Job A | OK     | 2s    |
| 2   | Job B | OK     | 5s    |
| 3   | Job C | FAIL   | 8s    |
| 4   | Job D | OK     | 1s    |
| 5   | Job E | OK     | 7s    |

---

## Código Python

```python
def hello():
    print("Hello World")

hello()
```

---

## Código TypeScript

```ts
interface User {
  id: string;
  email: string;
}

const user: User = {
  id: '1',
  email: 'user@example.com',
};
```

---

## Código JSON

```json
{
  "name": "Doc Flow",
  "version": "1.0.0",
  "features": ["markdown", "pdf", "playwright"]
}
```

---

## HTML Embutido

<div>
    <strong>Texto HTML</strong>
</div>

<script>
alert("isso deve sumir");
</script>

<iframe
    src="https://youtube.com"
></iframe>

---

## Caracteres Especiais

Acentuação:

- João
- São Paulo
- Café
- Informação

Símbolos:

© ® ™ € £ ¥

Emoji:

🚀
📄
🔥
🐍

---

## URL Muito Grande

https://example.com/a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/q/r/s/t/u/v/x/y/z

---

## Bloco de Texto Longo

Lorem ipsum dolor sit amet, consectetur adipiscing elit.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

---

## Imagem SVG

![SVG](https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg)

---

## Encerramento

Fim do documento de testes.
