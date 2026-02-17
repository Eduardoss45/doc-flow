import os


class Config:
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    TIMEZONE = os.getenv("TIMEZONE", "UTC")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 4000))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")


config = Config()
