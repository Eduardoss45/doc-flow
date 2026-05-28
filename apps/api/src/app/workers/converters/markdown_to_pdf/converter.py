from pathlib import Path

from jinja2 import Template

from .assets import process_assets
from .renderer import render_pdf
from .sanitize import sanitize_html
from .markdown_parser import (
    render_markdown,
    get_pygments_css,
)


def convert(
    input_path: str,
    output_path: str,
) -> None:
    input_file = Path(input_path)

    markdown_content = input_file.read_text(encoding="utf-8")

    html_body = render_markdown(markdown_content)

    html_body = sanitize_html(html_body)

    html_body = process_assets(html_body)

    pygments_css = get_pygments_css()

    fonts_dir = Path(__file__).parent / ".." / ".." / "fonts"

    font_url = (fonts_dir / "Roboto-Regular.ttf").resolve().as_uri()

    template_path = Path(__file__).parent / "templates" / "base.html"

    template = Template(template_path.read_text(encoding="utf-8"))

    html_document = template.render(
        content=html_body,
        pygments_css=pygments_css,
        font_url=font_url,
    )

    render_pdf(
        html_document=html_document,
        output_path=output_path,
    )
