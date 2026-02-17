import pandas as pd


def convert(input_path: str, output_path: str) -> None:
    try:
        df = pd.read_csv(input_path, encoding="utf-8", encoding_errors="replace")
    except UnicodeDecodeError:
        df = pd.read_csv(input_path, encoding="latin1")

    df.to_excel(output_path, index=False, engine="openpyxl")
