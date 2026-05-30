import requests
import tempfile

from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from app.config import config


def download_asset_to_temp_file(url: str, temp_dir: Path) -> tuple[Path, str] | None:
    with requests.get(url, stream=True, timeout=5, allow_redirects=False) as response:

        content_type = response.headers.get("Content-type", "").split(";")[0].lower()

        if content_type not in config.ALLOWED_IMAGE_TYPES:
            return None

        content_length = response.headers.get("Content-Length")

        if content_length:
            try:
                content_length_value = int(content_length)

            except ValueError:
                return None

            if content_length_value > config.MAX_IMAGE_SIZE:
                return None

        suffix_by_type = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/webp": ".webp",
            "image/gif": ".gif",
        }

        suffix = suffix_by_type.get(content_type, ".img")

        temp_file = tempfile.NamedTemporaryFile(
            dir=temp_dir,
            suffix=suffix,
            delete=False,
        )

        downloaded = 0

        with temp_file:
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue

                downloaded += len(chunk)

                if downloaded > config.MAX_IMAGE_SIZE:
                    Path(temp_file.name).unlink(missing_ok=True)
                    return None

                temp_file.write(chunk)
        return Path(temp_file.name), content_type


def is_allowed_asset_url(url: str) -> bool:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        return False

    hostname = parsed.hostname

    if not hostname:
        return False

    return hostname in config.ALLOWED_IMAGE_DOMAINS


def process_assets(html: str, temp_dir: Path) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for image in soup.find_all("img"):
        src = image.get("src")

        if not src or not is_allowed_asset_url(src):
            image.decompose()
            continue

        download = download_asset_to_temp_file(src, temp_dir)

        if not download:
            image.decompose()
            continue

        local_path, content_type = download

        image["src"] = local_path.resolve().as_uri()

    return str(soup)
