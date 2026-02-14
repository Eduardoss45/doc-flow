from dotenv import load_dotenv
import os

load_dotenv()

from flask import Flask, g, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery
from celery.schedules import crontab
from pathlib import Path
from uuid import UUID
from src.app.socket_manager import socketio, init_socketio
from src.repositories.document_repository import DocumentRepository
from src.repositories.client_storage_repository import ClientStorageRepository
from src.services.document_service import DocumentService
from src.http.documents.routes import documents_bp
from src.http.auth.routes import auth_bp
from infra.db.db import SessionLocal, engine, Base


celery = Celery(
    "document_processor",
    broker=os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    include=["src.workers.conversion_worker", "src.workers.cleanup_old_files"],
)

celery.conf.update(
    timezone=os.getenv("TIMEZONE", "UTC"),
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

celery.conf.beat_schedule = {
    "cleanup-expired-job": {
        "task": "src.workers.cleanup_old_files.cleanup_expired_files",
        "schedule": crontab(minute="*/1"),
    },
}


def create_app() -> Flask:
    app = Flask(__name__)
    Base.metadata.create_all(bind=engine)

    CORS(
        app,
        resources={
            r"/*": {
                "origins": [os.getenv("ALLOWED_ORIGINS")],
                "supports_credentials": True,
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "expose_headers": ["Set-Cookie"],
                "max_age": 600,
            }
        },
    )

    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["10 per second"],
        storage_uri=os.getenv("REDIS_URL", "memory://"),
        strategy="fixed-window",
        headers_enabled=True,
        retry_after=True,
    )

    init_socketio(app)

    @app.errorhandler(429)
    def ratelimit_handler(e):
        return (
            jsonify(
                {
                    "error": "Muitas requisições. Tente novamente mais tarde.",
                    "retry_after": e.description or "alguns segundos",
                }
            ),
            429,
        )

    @app.before_request
    def create_db_session():
        g.db = SessionLocal()
        g.document_repository = DocumentRepository(g.db)
        g.storage_repository = ClientStorageRepository(g.db)
        g.document_service = DocumentService(
            g.document_repository, g.storage_repository
        )

    @app.teardown_request
    def shutdown_db_session(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    app.extensions = getattr(app, "extensions", {})
    app.extensions["celery"] = celery
    app.extensions["limiter"] = limiter
    app.extensions["socketio"] = socketio

    register_blueprints(app)
    return app


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(documents_bp)
    app.register_blueprint(auth_bp)


if __name__ == "__main__":
    app = create_app()
    socketio.run(
        app,
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 4000)),
        debug=os.getenv("FLASK_DEBUG", "True").lower() == "true",
        use_reloader=False,
        log_output=True,
        allow_unsafe_werkzeug=True,
    )
