import base64
import requests

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from app.config import config


def is_allowed_asset_url(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        return False

    hostname = parsed.hostname

    if not hostname:
        return False

    return hostname in config.ALLOWED_IMAGE_DOMAINS


def process_assets(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    images = soup.find_all("img")

    for image in images:
        src = image.get("src")

        if not src:
            image.decompose()
            continue

        if not is_allowed_asset_url(src):
            image.decompose()
            continue

        try:
            response = requests.get(
                src,
                stream=True,
                timeout=5,
                allow_redirects=False,
            )

            content_type = response.headers.get("Content-Type", "").split(";")[0]

            if content_type not in config.ALLOWED_IMAGE_TYPES:
                image.decompose()
                continue

            content = response.content

            if len(content) > config.MAX_IMAGE_SIZE:
                image.decompose()
                continue

            encoded = base64.b64encode(content).decode()

            image["src"] = f"data:{content_type};base64,{encoded}"

        except Exception:
            image.decompose()

    return str(soup)
