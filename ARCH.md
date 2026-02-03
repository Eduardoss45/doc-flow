# Arquitetura

```bash
api/
├─ src/
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ main.py              # bootstrap da aplicação
│  │
│  │  ├─ http/                 # camada HTTP (controllers)
│  │  │  ├─ __init__.py
│  │  │  ├─ documents/
│  │  │  │  ├─ __init__.py
│  │  │  │  └─ routes.py
│  │  │  └─ health/
│  │  │     ├─ __init__.py
│  │  │     └─ routes.py
│  │
│  │  ├─ domain/              # regras e entidades puras
│  │  │  ├─ __init__.py
│  │  │  ├─ entities/
│  │  │  ├─ enums/
│  │  │  └─ value_objects/
│  │
│  │  ├─ services/            # orquestração de casos de uso
│  │  │  ├─ __init__.py
│  │  │  └─ document_service.py
│  │
│  │  ├─ repositories/        # acesso a dados (ORM)
│  │  │  ├─ __init__.py
│  │  │  └─ document_repository.py
│  │
│  │  ├─ infrastructure/      # detalhes técnicos
│  │  │  ├─ __init__.py
│  │  │  ├─ db/
│  │  │  ├─ cache/
│  │  │  ├─ queue/
│  │  │  └─ storage/
│  │
│  │  └─ workers/             # Celery
│  │     ├─ __init__.py
│  │     └─ conversion_worker.py
│  │
│  └─ __init__.py
│
├─ tests/
│
├─ pyproject.toml
└─ poetry.lock
```
