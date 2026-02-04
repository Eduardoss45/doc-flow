from markitdown import MarkItDown


def convert(input_path: str, output_path: str) -> None:
    md = MarkItDown()
    result = md.convert(input_path)
    print("PASSOU")

    # Opção recomendada (oficial):
    content = result.text_content

    # Alternativas (descomente uma se a primeira falhar):
    # content = result.markdown                  # se existir
    # content = str(result)                      # fallback (muito comum)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
