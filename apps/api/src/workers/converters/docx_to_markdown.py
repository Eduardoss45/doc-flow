from markitdown import MarkItDown


def convert(input_path: str, output_path: str) -> None:
    md = MarkItDown()
    result = md.convert(input_path)

    content = result.text_content

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
