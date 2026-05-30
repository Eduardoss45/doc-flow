import os


def parse_env_set(name: str) -> set[str]:
    value = os.getenv(name, "")

    return {item.strip().lower() for item in value.split(",") if item.strip()}


class Config:
    RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    TIMEZONE = os.getenv("TIMEZONE", "UTC")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*")
    FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.getenv("FLASK_PORT", 4000))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    ALLOWED_IMAGE_DOMAINS = parse_env_set("ALLOWED_IMAGE_DOMAINS")
    ALLOWED_IMAGE_TYPES = parse_env_set("ALLOWED_IMAGE_TYPES")
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", 5242880))
    MAX_MARKDOWN_SIZE = int(os.getenv("MAX_MARKDOWN_SIZE", 2 * 1024 * 1024))
    MAX_MARKDOWN_LINES = int(os.getenv("MAX_MARKDOWN_LINES", 20000))
    MAX_MARKDOWN_IMAGES = int(os.getenv("MAX_MARKDOWN_IMAGES", 20))
    MAX_RENDERED_HTML_SIZE = int(os.getenv("MAX_RENDERED_HTML_SIZE", 5 * 1024 * 1024))
    MAX_HTML_NODES = int(os.getenv("MAX_HTML_NODES", 50000))


config = Config()
