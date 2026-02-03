from flask import Flask, g
from src.infrastructure.db.db import SessionLocal, engine, Base
from src.repositories.document_repository import DocumentRepository
from src.services.document_service import DocumentService
from src.http.health.routes import health_bp
from src.http.documents.routes import documents_bp
from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
import os

load_dotenv()

celery = Celery(
    "document_processor",
    broker=os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["src.workers.conversion_worker","src.workers.cleanup_old_files"],
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

    register_blueprints(app)
    return app


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(documents_bp)
