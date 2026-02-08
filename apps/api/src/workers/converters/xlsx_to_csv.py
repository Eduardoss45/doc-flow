import pandas as pd


def convert(input_path: str, output_path: str) -> None:
    df = pd.read_excel(input_path, engine="openpyxl")
    df.to_csv(output_path, index=False, encoding="utf-8")
