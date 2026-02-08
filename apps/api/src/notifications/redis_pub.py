import os
import redis
import json


redis_client = None
NOTIFICATION_CHANNEL = "job_notifications"


def init_redis_client():
    """
    Inicializa o cliente Redis de forma lazy.
    Chame isso após load_dotenv() e antes de usar publish_job_event.
    """
    global redis_client
    if redis_client is not None:
        return

    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        raise ValueError(
            "REDIS_URL não definido no .env. "
            "Verifique seu arquivo .env ou defina a variável de ambiente."
        )

    print(f"[Redis Pub] Inicializando conexão com: {redis_url}")

    redis_client = redis.Redis.from_url(
        redis_url,
        decode_responses=True,
        socket_timeout=10,
        socket_connect_timeout=10,
        retry_on_timeout=True,
        health_check_interval=30,
    )

    try:
        pong = redis_client.ping()
        print(f"[Redis Pub] Conexão Redis OK (ping retornou: {pong})")
    except Exception as e:
        print(f"[Redis Pub] Falha ao conectar ao Redis: {e}")
        raise


def publish_job_event(event_type: str, data: dict):
    """
    Publica evento no Redis.
    Garante que o cliente esteja inicializado.
    """
    global redis_client
    if redis_client is None:
        init_redis_client()

    payload = {"type": event_type, "data": data}
    try:
        redis_client.publish(NOTIFICATION_CHANNEL, json.dumps(payload))
        print(f"[Redis Pub] Publicada {event_type} para client {data.get('client_id')}")
    except Exception as e:
        print(f"[Redis Pub] Erro ao publicar {event_type}: {e}")
