from fpdf import FPDF

def convert(input_path: str, output_path: str) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    with open(input_path, encoding='utf-8') as f:
        for line in f:
            pdf.multi_cell(0, 10, line.strip())
        pdf.output(output_path)