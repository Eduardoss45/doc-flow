from markitdown import MarkItDown

def convert(input_path: str, output_path: str) -> None:
    md = MarkItDown()
    markdown_content = md.convert(input_path)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)