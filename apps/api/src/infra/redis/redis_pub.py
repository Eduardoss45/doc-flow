import json
from .client import get_redis_client

NOTIFICATION_CHANNEL = "job_notifications"


def publish_job_event(event_type: str, data: dict):
    client = get_redis_client()
    payload = {"type": event_type, "data": data}
    try:
        client.publish(NOTIFICATION_CHANNEL, json.dumps(payload))
        print(f"[Redis Pub] Publicado {event_type} para {data.get('client_id')}")
    except Exception as e:
        print(f"[Redis Pub] Erro ao publicar: {e}")
