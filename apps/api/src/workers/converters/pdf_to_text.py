import pdfplumber


def convert(input_path: str, output_path: str) -> None:
    with pdfplumber.open(input_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text.strip())
