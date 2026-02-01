from src.app.main import create_app


def start():
    app = create_app()
    app.run(host="localhost", port=3000, debug=True)
