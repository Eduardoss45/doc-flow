from src.app.main import create_app
from src.app.celery_dev import start_celery_dev
import os


def start():
    if os.getenv("FLASK_ENV", "development") == "development":
        start_celery_dev()

    app = create_app()

    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", 3000))

    app.run(host=host, port=port, debug=True, use_reloader=False)
