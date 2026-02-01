from flask import Flask

from src.http.health.routes import health_bp
from src.http.documents.routes import documents_bp

from src.repositories.document_repository import DocumentRepository
from src.services.document_service import DocumentService


def create_app() -> Flask:
    app = Flask(__name__)

    document_repository = DocumentRepository()
    document_service = DocumentService(document_repository)

    app.extensions = getattr(app, "extensions", {})
    app.extensions["document_service"] = document_service

    register_blueprints(app)
    return app


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(documents_bp)
