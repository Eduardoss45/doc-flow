import time
import json
import redis.exceptions
from src.socket.core import socketio
from src.infra.redis.client import get_redis_client
from src.infra.redis.redis_pub import NOTIFICATION_CHANNEL


def start_redis_listener():
    print("[Redis Listener] Iniciando background task...")
    reconnect_delay = 5

    while True:
        try:
            client = get_redis_client()
            pubsub = client.pubsub()
            pubsub.subscribe(NOTIFICATION_CHANNEL)
            print("[Redis Listener] Subscrito ao canal com sucesso")

            for message in pubsub.listen():
                if message.get("type") != "message":
                    continue

                try:
                    payload = json.loads(message["data"])
                    event_type = payload.get("type")
                    data = payload.get("data", {})
                    client_id = data.get("client_id")

                    if not client_id or not event_type:
                        continue

                    if event_type == "job_completed":
                        socketio.emit("job_completed", data, room=client_id)
                    elif event_type == "job_failed":
                        socketio.emit("job_failed", data, room=client_id)
                    elif event_type == "job_progress":
                        socketio.emit("job_progress", data, room=client_id)
                    else:
                        continue

                    print(
                        f"[Redis Listener] Emitido {event_type} para room {client_id}"
                    )

                except json.JSONDecodeError:
                    print(f"[Redis Listener] JSON inválido: {message.get('data')}")
                except Exception as e:
                    print(f"[Redis Listener] Erro ao processar mensagem: {e}")

        except redis.exceptions.ConnectionError as e:
            print(
                f"[Redis Listener] Conexão perdida: {e}. "
                f"Reconectando em {reconnect_delay}s..."
            )
            time.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 60)

        except Exception as e:
            print(f"[Redis Listener] Erro crítico: {e}. Reiniciando em 10s...")
            time.sleep(10)
            reconnect_delay = 5
