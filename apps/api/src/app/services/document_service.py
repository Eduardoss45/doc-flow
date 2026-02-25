from __future__ import annotations

from uuid import UUID
from pathlib import Path
from typing import TYPE_CHECKING
from app.domain.entities.document_job import DocumentJob
from app.domain.enums.conversion_type import ConversionType
from app.infra.utils import get_client_input_dir, get_client_output_dir

if TYPE_CHECKING:
    from app.repositories.document_repository import DocumentRepository
    from app.repositories.client_storage_repository import ClientStorageRepository


class DocumentService:
    def __init__(
        self,
        job_repository: DocumentRepository,
        storage_repository: ClientStorageRepository,
    ):
        self.job_repo = job_repository
        self.storage_repo = storage_repository

    def create_job(
        self,
        client_id: UUID,
        conversion_type: ConversionType,
        input_filename: str,
    ) -> DocumentJob:
        job = DocumentJob(
            conversion_type=conversion_type,
            input_filename=input_filename,
            input_path="",
        )

        input_dir = get_client_input_dir(client_id)
        output_dir = get_client_output_dir(client_id)

        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        input_path = input_dir / f"{job.id}_{input_filename}"
        job.input_path = str(input_path)

        ext_map = {
            ConversionType.CSV_TO_JSON: "json",
            ConversionType.CSV_TO_XLSX: "xlsx",
            ConversionType.XLSX_TO_CSV: "csv",
            ConversionType.TXT_TO_PDF: "pdf",
            ConversionType.PDF_TO_TEXT: "txt",
            ConversionType.DOCX_TO_PDF: "pdf",
            ConversionType.DOCX_TO_MARKDOWN: "md",
        }
        ext = ext_map.get(conversion_type, "out")
        job.output_path = str(output_dir / f"{job.id}.{ext}")

        self.job_repo.save(job)
        return job
