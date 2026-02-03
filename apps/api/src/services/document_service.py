from uuid import UUID
from pathlib import Path

from src.domain.entities import DocumentJob
from src.domain.enums import ConversionType
from src.repositories.document_repository import DocumentRepository

class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    def create_job(
        self,
        conversion_type: ConversionType,
        input_path: str,
        input_filename: str,
    ) -> DocumentJob:
        job = DocumentJob(
            conversion_type=conversion_type,
            input_path=input_path,
            input_filename=input_filename,
        )

        ext_map = {
            ConversionType.CSV_TO_JSON: 'json',
            ConversionType.CSV_TO_XLSX: 'xlsx',
            ConversionType.XLSX_TO_CSV: 'csv',
            ConversionType.TXT_TO_PDF: 'pdf',
            ConversionType.PDF_TO_TEXT: 'txt',
            ConversionType.DOCX_TO_PDF: 'pdf',
            ConversionType.DOCX_TO_MARKDOWN: 'md',
        }
        ext = ext_map.get(conversion_type, 'out')
        output_dir = Path("src/infrastructure/storage/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        job.output_path = str(output_dir / f"{job.id}.{ext}")

        self.repository.save(job)
        return job