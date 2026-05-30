import re
from bs4 import BeautifulSoup
from app.config import config

MARKDOWN_IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\([^)]+\)")


def validate_markdown_limits(markdown_content: str) -> None:
    content_size = len(markdown_content.encode("utf-8"))

    if content_size > config.MAX_MARKDOWN_SIZE:
        raise ValueError("Markdown exceeds maximum allowed size")

    line_count = markdown_content.count("\n") + 1

    if line_count > config.MAX_MARKDOWN_LINES:
        raise ValueError("Markdown exceeds maximum number of lines")

    image_count = len(MARKDOWN_IMAGE_PATTERN.findall(markdown_content))

    if image_count > config.MAX_MARKDOWN_IMAGES:
        raise ValueError("Markdown exceeds maximum number of images")


def validate_html_limits(html: str) -> None:
    html_size = len(html.encode("utf-8"))

    if html_size > config.MAX_RENDERED_HTML_SIZE:
        raise ValueError("Rendered HTML exceeds maximum allowed size")

    soup = BeautifulSoup(html, "html.parser")
    node_count = len(soup.find_all())

    if node_count > config.MAX_HTML_NODES:
        raise ValueError("Rendered HTML exceeds maximum number of nodes")
