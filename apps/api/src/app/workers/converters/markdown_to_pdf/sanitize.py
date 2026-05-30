import bleach

from bs4 import BeautifulSoup

ALLOWED_TAGS = [
    "p",
    "h1",
    "h2",
    "h3",
    "h4",
    "ul",
    "ol",
    "li",
    "strong",
    "em",
    "blockquote",
    "code",
    "pre",
    "table",
    "thead",
    "tbody",
    "tr",
    "td",
    "th",
    "a",
    "img",
    "hr",
    "br",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
    "img": ["src", "alt"],
    "code": ["class"],
}


def remove_dangerous_nodes(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for node in soup.find_all(["script", "style", "iframe", "object", "embed"]):
        node.decompose()

    return str(soup)


def sanitize_html(html: str) -> str:
    html = remove_dangerous_nodes(html)

    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=["http", "https"],
        strip=True,
    )
