import tempfile
from pathlib import Path

from jinja2 import Template

from app.config import config

from .assets import process_assets
from .renderer import render_pdf
from .sanitize import sanitize_html
from .markdown_parser import (
    render_markdown,
    get_pygments_css,
)

from .limits import (
    validate_markdown_limits,
    validate_html_limits,
)


def convert(
    input_path: str,
    output_path: str,
) -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_assets_dir = Path(temp_dir)

        input_file = Path(input_path)

        markdown_content = input_file.read_text(encoding="utf-8")

        validate_markdown_limits(markdown_content)

        html_body = render_markdown(markdown_content)

        html_body = sanitize_html(html_body)

        validate_html_limits(html_body)

        html_body = process_assets(
            html_body,
            temp_assets_dir,
        )

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

        if config.MARKDOWN_PDF_DEBUG_HTML:
            debug_path = Path(output_path).with_suffix(".debug.html")
            debug_path.write_text(html_document, encoding="utf-8")

        html_file = temp_assets_dir / "document.html"
        html_file.write_text(html_document, encoding="utf-8")

        render_pdf(
            html_file=html_file,
            output_path=output_path,
            allowed_asset_dirs=[
                temp_assets_dir,
                fonts_dir.resolve(),
            ],
        )
