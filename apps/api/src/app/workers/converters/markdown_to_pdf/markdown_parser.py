from markdown_it import MarkdownIt

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.lexers.special import TextLexer


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


def render_markdown(markdown_content: str) -> str:
    md = MarkdownIt(
        "commonmark",
        {
            "highlight": highlight_code,
        },
    )

    return md.render(markdown_content)


def get_pygments_css() -> str:
    formatter = HtmlFormatter(
        style="friendly",
        cssclass="highlight",
    )

    return formatter.get_style_defs(".highlight")
