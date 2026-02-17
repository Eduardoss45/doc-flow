from app.factory import create_app
from app.realtime.server import socketio, init_socketio
from app.config import config


def main():
    app = create_app()

    init_socketio(app)

    print(f"[API + Socket.IO] Iniciando em {config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"[Ambiente] {config.FLASK_ENV} | Debug: {config.FLASK_DEBUG}")

    socketio.run(
        app,
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
        use_reloader=False,
        log_output=True,
        allow_unsafe_werkzeug=True,
    )


if __name__ == "__main__":
    main()
