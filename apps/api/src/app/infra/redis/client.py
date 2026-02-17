import os
import redis
import threading

_redis_client = None
_redis_lock = threading.Lock()


def get_redis_client() -> redis.Redis:
    """
    Retorna um cliente Redis thread-safe (lazy init + lock).
    Usa decode_responses=True por padrão.
    """
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    with _redis_lock:
        if _redis_client is not None:
            return _redis_client

        url = os.getenv("REDIS_URL")
        if not url:
            raise ValueError("REDIS_URL não definido no ambiente")

        print(f"[Redis Client] Conectando em: {url}")
        client = redis.Redis.from_url(
            url,
            decode_responses=True,
            socket_timeout=10,
            socket_connect_timeout=10,
            retry_on_timeout=True,
            health_check_interval=30,
        )

        try:
            client.ping()
            print("[Redis Client] Conexão OK")
        except Exception as e:
            print(f"[Redis Client] Falha na conexão: {e}")
            raise

        _redis_client = client
        return client
