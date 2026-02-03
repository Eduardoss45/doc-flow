from celery import shared_task
from pathlib import Path
import importlib

from src.infrastructure.db.db import SessionLocal
from src.repositories.document_repository import DocumentRepository
from src.domain.enums.conversion_type import ConversionType
from src.domain.entities.document_job import DocumentJob


CONVERTERS = {
    ConversionType.CSV_TO_JSON:       'csv_to_json.convert',
    ConversionType.CSV_TO_XLSX:       'csv_to_xlsx.convert',
    ConversionType.XLSX_TO_CSV:       'xlsx_to_csv.convert',
    ConversionType.TXT_TO_PDF:        'txt_to_pdf.convert',
    ConversionType.PDF_TO_TEXT:       'pdf_to_text.convert',
    ConversionType.DOCX_TO_PDF:       'docx_to_pdf.convert',
    ConversionType.DOCX_TO_MARKDOWN:  'docx_to_markdown.convert',
}


@shared_task(name="process_conversion")
def process_conversion(job_id: str):
    db = SessionLocal()
    repo = DocumentRepository(db)

    try:
        job: DocumentJob = repo.get_by_id(job_id)
        if not job:
            return

        job.mark_processing()
        repo.update(job)

        input_path = Path(job.input_path)
        output_path = Path(job.output_path)

        module_name, func_name = CONVERTERS[
            ConversionType(job.conversion_type)
        ].rsplit('.', 1)

        converter_module = importlib.import_module(
            f'src.workers.converters.{module_name}'
        )
        convert_func = getattr(converter_module, func_name)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        convert_func(str(input_path), str(output_path))

        job.mark_completed(str(output_path))

    except Exception as e:
        job.mark_failed(str(e))
        if output_path and output_path.exists():
            output_path.unlink()

    finally:
        repo.update(job)
        if input_path.exists():
            input_path.unlink(missing_ok=True)
        db.close()
