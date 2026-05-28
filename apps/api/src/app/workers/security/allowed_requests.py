from urllib.parse import urlparse
from app.config import ALLOWED_IMAGE_DOMAINS


def is_allowed_request(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        return False

    hostname = parsed.hostname

    if not hostname:
        return False

    return hostname in ALLOWED_IMAGE_DOMAINS
