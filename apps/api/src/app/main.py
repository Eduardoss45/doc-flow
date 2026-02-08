from src.repositories.document_repository import DocumentRepository
from infrastructure.db.db import SessionLocal, engine, Base
from src.services.document_service import DocumentService
from src.http.documents.routes import documents_bp
from flask_limiter.util import get_remote_address
from src.http.health.routes import health_bp
from flask import Flask, g, request, jsonify
from celery.schedules import crontab
from flask_limiter import Limiter
from dotenv import load_dotenv
from flask_cors import CORS
from celery import Celery
from pathlib import Path
import os


load_dotenv()

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
        g.document_service = DocumentService(g.document_repository)

    @app.teardown_request
    def shutdown_db_session(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    app.extensions = getattr(app, "extensions", {})
    app.extensions["celery"] = celery
    app.extensions["limiter"] = limiter
    register_blueprints(app)
    return app


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(documents_bp)


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv("FLASK_HOST", "0.0.0.0"),
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "True").lower() == "true",
        use_reloader=True,
    )
