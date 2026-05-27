from pathlib import Path

from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers.special import TextLexer
import bleach


def highlight_code(code: str, lang: str | None, attrs=None) -> str:
    try:
        lexer = get_lexer_by_name(lang or "text")
    except Exception:
        lexer = TextLexer()

    formatter = HtmlFormatter(
        style="friendly",
        cssclass="highlight",
    )

    return highlight(code, lexer, formatter)


def convert(input_path: str, output_path: str) -> None:
    input_file = Path(input_path)
    output_file = Path(output_path)

    markdown_content = input_file.read_text(encoding="utf-8")

    md = MarkdownIt(
        "commonmark",
        {
            "highlight": highlight_code,
        },
    )
    html_body = md.render(markdown_content)

    html_body = bleach.clean(
        html_body,
        tags=[
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
        ],
        attributes={
            "a": ["href", "title"],
            "img": ["src", "alt"],
            "code": ["class"],
        },
        protocols=["http", "https"],
        strip=True,
    )

    formatter = HtmlFormatter(
        style="friendly",
        cssclass="highlight",
    )

    pygments_css = formatter.get_style_defs(".highlight")

    html_document = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8" />
        <style>
            {pygments_css}

            body {{
                font-family: Arial, sans-serif;
                padding: 32px;
                line-height: 1.6;
                color: #111;
            }}

            pre {{
                background: #f5f5f5;
                padding: 12px;
                overflow-x: auto;
                border-radius: 8px;
                white-space: pre-wrap;
                word-break: break-word;
            }}

            code {{
                font-family: monospace;
            }}

            h1, h2, h3 {{
                margin-top: 24px;
            }}

            table {{
                border-collapse: collapse;
                width: 100%;
            }}

            table, th, td {{
                border: 1px solid #ccc;
            }}

            th, td {{
                padding: 8px;
            }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        page = browser.new_page()

        page.set_content(
            html_document,
            wait_until="networkidle",
        )

        page.pdf(
            path=str(output_file),
            format="A4",
            print_background=True,
        )

        browser.close()
