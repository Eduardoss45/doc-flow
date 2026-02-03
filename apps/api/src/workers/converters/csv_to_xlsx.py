import pandas as pd

def convert(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path, encoding='utf-8')
    df.to_excel(output_path, index=False, engine='openpyxl')