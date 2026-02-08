# Sistema de Bloqueio com Blacklist + Cache (Redis)

## Visão Geral

Este projeto implementa um mecanismo simples e eficaz de **bloqueio temporário de clientes** (baseado no `client_id` anônimo) para prevenir abusos, como:

- Tentativas de DoS / flood de requisições
- Múltiplas conexões WebSocket simultâneas excessivas
- Uploads em loop rápido para esgotar quota ou recursos

O bloqueio é feito via **blacklist** armazenada no Redis (cache de alta performance), com expiração automática.

### Principais características

- Bloqueio por `client_id` (UUID gerado no cookie HttpOnly)
- Duração configurável (ex: 1 hora, 24 horas)
- Contador de ações suspeitas antes de bloquear (ex: > 10 conexões/minuto)
- Expiração automática (não precisa de limpeza manual)
- Leve e escalável (Redis suporta milhões de chaves)
- Fácil de integrar em endpoints HTTP, WebSocket e Celery tasks

## Motivação

- O `client_id` é temporário (expira em 24h) e anônimo → não afeta usuários reais
- Limite de taxa existente (10 req/s via Flask-Limiter) protege contra flood bruto
- Mas ainda é possível abusar com muitas conexões WebSocket rápidas ou uploads espaçados
- Blacklist no Redis permite bloquear completamente um client_id malicioso sem impacto em usuários legítimos

## Como funciona

1. **Contador de ações suspeitas**  
   Chave Redis: `conn_count:{client_id}`  
   Incrementa a cada conexão/ação relevante (ex: nova conexão WS, upload)  
   Expiração: 60 segundos (janela deslizante)

2. **Limite atingido → entra na blacklist**  
   Quando o contador ultrapassa o limite (ex: 15 em 60s):  
   Cria chave `blacklist:{client_id}` com valor `"1"` e expiração (ex: 3600s = 1h)

3. **Verificação em endpoints críticos**  
   Antes de processar requisição/conexão:
   - Se `blacklist:{client_id}` existe → bloqueia imediatamente (401/403 ou desconecta WS)

4. **Expiração automática**  
   Tanto o contador quanto a blacklist expiram sozinhos → sem job de limpeza necessário

## Implementação sugerida (Flask + Redis + Socket.IO)

### Dependências

```bash
pip install redis flask-socketio
```

### Configuração básica (no seu app principal)

```python
import redis
from flask import request
from flask_socketio import disconnect

# Conexão Redis (use o mesmo do Celery ou crie um novo)
redis_client = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))

# Configurações
MAX_CONNECTIONS_PER_MINUTE = 15
BLACKLIST_DURATION_SECONDS = 3600  # 1 hora
CONNECTION_WINDOW_SECONDS = 60
```

### Middleware para HTTP (exemplo em endpoint ou before_request)

```python
@app.before_request
def check_blacklist():
    if request.path in ['/documents/upload', '/documents/my-jobs']:  # endpoints críticos
        client_id = request.cookies.get("client_id")
        if not client_id:
            return jsonify({"error": "client_id required"}), 401

        blacklist_key = f"blacklist:{client_id}"
        if redis_client.exists(blacklist_key):
            return jsonify({"error": "Acesso temporariamente bloqueado por uso indevido"}), 403
```

### Para WebSocket (Socket.IO)

```python
@socketio.on('connect')
def handle_connect():
    client_id = request.cookies.get("client_id")
    if not client_id:
        emit('auth_error', {'message': 'client_id required'})
        return False

    blacklist_key = f"blacklist:{client_id}"
    if redis_client.exists(blacklist_key):
        emit('blocked', {'message': 'Seu acesso foi bloqueado temporariamente'})
        disconnect()
        return False

    # Contador de conexões
    conn_key = f"conn_count:{client_id}"
    redis_client.incr(conn_key)
    redis_client.expire(conn_key, CONNECTION_WINDOW_SECONDS)

    count = int(redis_client.get(conn_key) or 0)
    if count > MAX_CONNECTIONS_PER_MINUTE:
        redis_client.set(blacklist_key, "1", ex=BLACKLIST_DURATION_SECONDS)
        emit('blocked', {'message': 'Limite de conexões excedido. Tente novamente mais tarde.'})
        disconnect()
        return False

    join_room(client_id)
    emit('connected', {'client_id': client_id})
```

### Função auxiliar para bloquear manualmente (opcional)

```python
def block_client(client_id: str, duration_seconds: int = BLACKLIST_DURATION_SECONDS):
    key = f"blacklist:{client_id}"
    redis_client.set(key, "1", ex=duration_seconds)
```

### Monitoramento / Logs

Adicione logs quando bloquear:

```python
import logging

logger = logging.getLogger(__name__)

# No momento do bloqueio:
logger.warning(f"Client {client_id} bloqueado por excesso de conexões. Contador: {count}")
```

## Cuidados e boas práticas

- **Nunca bloqueie permanentemente** → sempre com expiração
- **Não exponha o motivo exato** no erro para evitar fingerprinting
- **Teste com múltiplas abas / dispositivos** (o mesmo client_id pode vir de vários lugares)
- **Limpe chaves antigas** (opcional): crie um job Celery que remove blacklists expiradas (mas Redis já faz isso)
- **Integre com Flask-Limiter** para proteção em camadas
- **Em produção**: use Redis com senha + TLS se expor externamente

## Extensões futuras

- Contador por tipo de ação (ex: upload vs WS connect)
- Bloqueio progressivo (1h → 6h → 24h)
- Notificação no admin quando alguém é bloqueado
- Integração com fail2ban ou WAF se precisar de proteção mais pesada

Esse mecanismo é reutilizável em qualquer projeto que use client_id anônimo ou sessão temporária.

Boa sorte com a implementação!
