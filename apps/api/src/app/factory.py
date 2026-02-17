from flask import Flask, g, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_smorest import Api
from marshmallow import ValidationError

from app.config import config
from app.realtime.server import socketio, init_socketio
from app.infra.db.db import SessionLocal, engine, Base
from app.repositories.document_repository import DocumentRepository
from app.repositories.client_storage_repository import ClientStorageRepository
from app.services.document_service import DocumentService
from app.http.documents.routes import documents_bp
from app.http.auth.routes import auth_bp
from app.workers.celery_app import celery


def create_app() -> Flask:
    app = Flask(__name__)

    Base.metadata.create_all(bind=engine)

    app.config["API_TITLE"] = "Doc flow API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/docs"
    app.config["OPENAPI_JSON_PATH"] = "openapi.json"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )
    app.config["OPENAPI_REDOC_PATH"] = "/redoc"

    api = Api(app)

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return (
            jsonify(
                {
                    "error": "Erro de validação",
                    "messages": err.messages,
                }
            ),
            422,
        )

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

    init_socketio(app)

    @app.before_request
    def create_db_session():
        g.db = SessionLocal()
        g.document_repository = DocumentRepository(g.db)
        g.storage_repository = ClientStorageRepository(g.db)
        g.document_service = DocumentService(
            g.document_repository,
            g.storage_repository,
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

    api.register_blueprint(documents_bp)
    api.register_blueprint(auth_bp)

    return app
