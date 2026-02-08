# BUGS E MELHORIAS

- não permitir entrada errada deacordo com o tipo de conversão.
- retornar feedback em caso de falha para atualizar o frontend.
- não permitir mais de um request no frontend.

## Client ID anônimo (cookie ou header)

### Como funciona

1. No primeiro acesso:

   * Backend gera um `client_id` (UUID)
2. Envia para o frontend:

   * via cookie **ou**
   * via header (`X-Client-Id`)
3. Frontend reaproveita por 24h
4. Backend associa jobs a esse `client_id`

Isso resolve:

* Sessão de 24h
* Isolamento de arquivos
* Sem usuários
* Sem autenticação
* Sem estado complexo

---

## Arquitetura recomendada (simples e limpa)

### 1️⃣ Client ID

```text
client_id = UUID v4
TTL lógico = 24h
```

### 2️⃣ Onde armazenar

Escolha **um**:

#### Opção A — Cookie (mais simples)

* Cookie HTTP-only
* Expira em 24h

#### Opção B — LocalStorage + Header

* Frontend guarda
* Envia em todas as requisições

---

## Exemplo de fluxo (backend)

### Middleware Flask

```python
from uuid import uuid4
from flask import request, g, make_response

@app.before_request
def identify_client():
    client_id = request.cookies.get("client_id")

    if not client_id:
        client_id = str(uuid4())
        g.new_client_id = client_id
    else:
        g.new_client_id = None

    g.client_id = client_id
```

### Após resposta

```python
@app.after_request
def set_client_cookie(response):
    if getattr(g, "new_client_id", None):
        response.set_cookie(
            "client_id",
            g.client_id,
            max_age=86400,  # 24h
            httponly=True,
            samesite="Lax",
        )
    return response
```

---

## 3️⃣ Associar jobs ao client_id

### Model

```python
client_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
```

### DocumentJob

```python
client_id: UUID
```

### Create job

```python
job = DocumentJob(
    client_id=g.client_id,
    conversion_type=conversion_type,
    ...
)
```

---

## Cleanup fica trivial

```sql
DELETE FROM document_jobs
WHERE expires_at < NOW();
```

Ou por cliente:

```sql
DELETE FROM document_jobs
WHERE client_id = :client_id
  AND expires_at < NOW();
```

---

## Comparação direta

| Estratégia    | Recomendada? | Motivo                           |
| ------------- | ------------ | -------------------------------- |
| IP            | ❌            | Instável, não identifica cliente |
| Session Flask | ⚠️           | Estado no backend                |
| JWT anônimo   | ⚠️           | Overkill                         |
| Cookie + UUID | ✅            | Simples, robusto                 |
| Login         | ❌            | Fora do escopo                   |

---

## Conclusão objetiva

* ❌ IP **não** é uma boa ideia
* ✅ UUID anônimo por cookie/header é **a melhor solução**
* ✔️ Não adiciona usuários
* ✔️ Mantém sessão por 24h
* ✔️ Simplifica cleanup
* ✔️ Arquiteturalmente correta

Se quiser, posso:

* adaptar seu código atual para `client_id`
* ou desenhar o fluxo frontend ↔ backend completo

Mas a decisão técnica correta aqui é clara.
