from src.app.main import create_app
import os


def start():
    app = create_app()

    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", 3000))

    app.run(host=host, port=port, debug=True)
