import subprocess
import os


def convert(input_path: str, output_path: str) -> None:
    cmd = [
        "soffice",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        os.path.dirname(output_path),
        input_path,
    ]
    subprocess.run(cmd, check=True)
