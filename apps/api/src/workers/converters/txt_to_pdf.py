from fpdf import FPDF
from pathlib import Path


def convert(input_path: str | Path, output_path: str | Path) -> None:
    pdf = FPDF()
    pdf.add_page()

    pdf.add_font(
        family="Roboto-Regular",
        style="",
        fname="src/workers/fonts/Roboto-Regular.ttf",
        uni=True,
    )
    pdf.set_font("Roboto-Regular", size=12)

    input_path = Path(input_path)
    with input_path.open(encoding="utf-8") as f:
        text = f.read()

    pdf.multi_cell(
        w=0,
        h=6,
        txt=text,
        align="L",
        markdown=False,
    )

    pdf.output(output_path)
