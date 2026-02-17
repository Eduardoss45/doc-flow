from enum import Enum


class ConversionType(str, Enum):
    CSV_TO_JSON = "csv_to_json"
    CSV_TO_XLSX = "csv_to_xlsx"
    XLSX_TO_CSV = "xlsx_to_csv"
    TXT_TO_PDF = "txt_to_pdf"
    PDF_TO_TEXT = "pdf_to_text"
    DOCX_TO_PDF = "docx_to_pdf"
    DOCX_TO_MARKDOWN = "docx_to_markdown"
