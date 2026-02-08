from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from uuid import UUID
import os
import redis
import json
import time
from src.notifications.redis_pub import (
    redis_client,
    NOTIFICATION_CHANNEL,
    init_redis_client,
)


socketio = SocketIO(
    cors_allowed_origins=os.getenv("ALLOWED_ORIGINS", "*"),
    manage_session=False,
)


def init_socketio(app):
    """
    Inicializa SocketIO e Redis de forma síncrona.
    Inicia o listener como background task do SocketIO (sem thread manual).
    """

    init_redis_client()

    socketio.init_app(app)

    socketio.start_background_task(target=start_redis_listener)

    print(
        "[Socket.IO] Inicialização completa. Listener Redis iniciado como background task."
    )


def start_redis_listener():
    """
    Listener seguro usando start_background_task (ordem garantida).
    """
    print("[Socket.IO] Iniciando listener Redis para notificações de jobs...")

    while True:
        try:
            pubsub = redis_client.pubsub()
            pubsub.subscribe(NOTIFICATION_CHANNEL)
            print("[Socket.IO] Conectado ao canal Redis com sucesso")

            for message in pubsub.listen():
                if message.get("type") == "message":
                    try:
                        payload = json.loads(message["data"])
                        event_type = payload.get("type")
                        data = payload.get("data", {})
                        client_id = data.get("client_id")

                        if not client_id:
                            continue

                        if event_type == "job_completed":
                            socketio.emit("job_completed", data, room=client_id)
                            print(
                                f"[Socket.IO] Emitido job_completed para client {client_id}"
                            )
                        elif event_type == "job_failed":
                            socketio.emit("job_failed", data, room=client_id)
                            print(
                                f"[Socket.IO] Emitido job_failed para client {client_id}"
                            )
                        elif event_type == "job_progress":
                            socketio.emit("job_progress", data, room=client_id)
                            print(
                                f"[Socket.IO] Emitido job_progress para client {client_id}"
                            )
                    except json.JSONDecodeError:
                        print(f"[Socket.IO] JSON inválido recebido: {message['data']}")
                    except Exception as e:
                        print(f"[Socket.IO] Erro ao processar mensagem Redis: {e}")

        except redis.exceptions.ConnectionError as e:
            print(
                f"[Socket.IO] Falha na conexão Redis: {e}. Tentando reconectar em 5s..."
            )
            time.sleep(5)
        except Exception as e:
            print(f"[Socket.IO] Erro crítico no listener: {e}. Reiniciando em 10s...")
            time.sleep(10)


@socketio.on("connect")
def handle_connect():
    client_id = request.cookies.get("client_id")
    if not client_id:
        emit("auth_error", {"message": "client_id required"})
        return False

    try:
        UUID(client_id)
    except ValueError:
        emit("auth_error", {"message": "client_id inválido"})
        return False

    join_room(client_id)
    emit("connected", {"message": "Conectado com sucesso", "client_id": client_id})
    print(f"[Socket.IO] Client {client_id} conectado")


@socketio.on("disconnect")
def handle_disconnect():
    client_id = request.cookies.get("client_id")
    if client_id:
        leave_room(client_id)
        print(f"[Socket.IO] Client {client_id} desconectado")
