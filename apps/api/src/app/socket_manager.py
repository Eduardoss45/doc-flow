from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from uuid import UUID
import os
import redis
import json
import time
import threading
from src.notifications.redis_pub import NOTIFICATION_CHANNEL, init_redis_client


socketio = SocketIO(
    cors_allowed_origins=os.getenv("ALLOWED_ORIGINS", "*"),
    manage_session=False,
    async_mode="threading",
    logger=True,
    engineio_logger=True,
)


# Lock para proteger acesso ao redis_client em múltiplas threads
redis_lock = threading.Lock()
redis_client_local = None  # Vamos usar uma variável local por thread se necessário


def get_redis_client():
    """Garante que redis_client esteja inicializado na thread atual"""
    global redis_client_local
    if redis_client_local is None:
        with redis_lock:
            if redis_client_local is None:
                print("[Redis] Inicializando cliente na thread atual...")
                init_redis_client()  # chama a função original que seta o global
                # Se sua init_redis_client seta um global chamado redis_client, pegamos ele
                from src.notifications.redis_pub import redis_client as global_client

                redis_client_local = global_client
                if redis_client_local is None:
                    raise RuntimeError("Falha ao inicializar redis_client")
    return redis_client_local


def init_socketio(app):
    # Inicializa Redis na thread principal (garantia extra)
    get_redis_client()  # força inicialização cedo
    socketio.init_app(app)
    socketio.start_background_task(target=start_redis_listener)
    print("[Socket.IO] Inicialização completa. Listener Redis iniciado.")


def start_redis_listener():
    print("[Socket.IO] Iniciando listener Redis em thread separada...")

    while True:
        try:
            client = get_redis_client()  # sempre pega o cliente atualizado
            pubsub = client.pubsub()
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
                            print(f"[Socket.IO] Emitido job_completed para {client_id}")
                        elif event_type == "job_failed":
                            socketio.emit("job_failed", data, room=client_id)
                            print(f"[Socket.IO] Emitido job_failed para {client_id}")
                        elif event_type == "job_progress":
                            socketio.emit("job_progress", data, room=client_id)
                            print(f"[Socket.IO] Emitido job_progress para {client_id}")
                    except json.JSONDecodeError:
                        print(f"[Socket.IO] JSON inválido: {message['data']}")
                    except Exception as e:
                        print(f"[Socket.IO] Erro ao processar mensagem: {e}")

        except redis.exceptions.ConnectionError as e:
            print(f"[Socket.IO] Falha na conexão Redis: {e}. Reconectando em 5s...")
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
