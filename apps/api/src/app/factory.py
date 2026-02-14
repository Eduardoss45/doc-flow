from flask import Flask, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from src.app.config import config
from src.socket.server import socketio, init_socketio
from src.infra.db.db import SessionLocal, engine, Base
from src.repositories.document_repository import DocumentRepository
from src.repositories.client_storage_repository import ClientStorageRepository
from src.services.document_service import DocumentService
from src.http.documents.routes import documents_bp
from src.http.auth.routes import auth_bp
from src.workers.celery_app import celery


def create_app() -> Flask:
    app = Flask(__name__)
    Base.metadata.create_all(bind=engine)

    CORS(
        app,
        resources={
            r"/*": {
                "origins": [config.ALLOWED_ORIGINS],
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
        storage_uri=config.REDIS_URL,
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

    app.extensions["celery"] = celery
    app.extensions["limiter"] = limiter
    app.extensions["socketio"] = socketio

    app.register_blueprint(documents_bp)
    app.register_blueprint(auth_bp)

    return app
