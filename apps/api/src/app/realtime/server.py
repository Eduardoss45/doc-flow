from flask import request
from uuid import UUID
from .core import socketio
from flask_socketio import join_room, leave_room, emit


def init_socketio(app):
    """
    Inicializa o Socket.IO no app Flask e agenda o listener Redis
    como background task.
    """
    socketio.init_app(app)

    from .redis_listener import start_redis_listener

    socketio.start_background_task(target=start_redis_listener)
    print("[Socket.IO] Inicializado + listener Redis agendado como background task")


@socketio.on("connect")
def handle_connect(auth=None):
    client_id = request.cookies.get("client_id")
    if not client_id:
        emit("auth_error", {"message": "client_id obrigatório"})
        return False

    try:
        UUID(client_id)
    except ValueError:
        emit("auth_error", {"message": "client_id inválido"})
        return False

    join_room(client_id)
    emit("connected", {"message": "Conectado", "client_id": client_id})
    print(f"[Socket] Client conectado: {client_id}")


@socketio.on("disconnect")
def handle_disconnect():
    client_id = request.cookies.get("client_id")
    if client_id:
        leave_room(client_id)
        print(f"[Socket] Client desconectado: {client_id}")
