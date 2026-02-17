from app.workers.celery_app import celery
from pathlib import Path
import importlib
from uuid import UUID
from app.infra.db.db import SessionLocal
from app.repositories.document_repository import DocumentRepository
from app.repositories.client_storage_repository import ClientStorageRepository
from app.domain.enums.conversion_type import ConversionType
from app.domain.entities.document_job import DocumentJob
from app.infra.utils import (
    get_client_input_dir,
    get_client_output_dir,
    get_directory_size,
)
from app.infra.redis.redis_pub import publish_job_event


CONVERTERS = {
    ConversionType.CSV_TO_JSON: "csv_to_json.convert",
    ConversionType.CSV_TO_XLSX: "csv_to_xlsx.convert",
    ConversionType.XLSX_TO_CSV: "xlsx_to_csv.convert",
    ConversionType.TXT_TO_PDF: "txt_to_pdf.convert",
    ConversionType.PDF_TO_TEXT: "pdf_to_text.convert",
    ConversionType.DOCX_TO_PDF: "docx_to_pdf.convert",
    ConversionType.DOCX_TO_MARKDOWN: "docx_to_markdown.convert",
}


@celery.task(name="process_conversion")
def process_conversion(job_id: str, client_id: str):
    db = SessionLocal()
    job_repo = DocumentRepository(db)
    storage_repo = ClientStorageRepository(db)

    try:
        job_uuid = UUID(job_id)
        job = job_repo.get_by_id(job_uuid)
        if not job:
            return

        job.mark_processing()
        job_repo.update(job)

        input_path = Path(job.input_path)
        output_path = Path(job.output_path) if job.output_path else None

        if not output_path:
            raise ValueError("output_path não definido no job")

        module_name, func_name = CONVERTERS[ConversionType(job.conversion_type)].rsplit(
            ".", 1
        )
        converter_module = importlib.import_module(
            f"app.workers.converters.{module_name}"
        )
        convert_func = getattr(converter_module, func_name)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        convert_func(str(input_path), str(output_path))

        job.mark_completed(str(output_path))
        print("Passou")
        publish_job_event(
            "job_completed",
            {
                "job_id": str(job.id),
                "status": job.status.value,
                "download_url": f"/documents/download/{job.id}",
                "filename": job.input_filename,
                "client_id": client_id,
            },
        )

        job_repo.update(job)

        client_dir = get_client_output_dir(client_id)
        new_size = get_directory_size(client_dir)
        storage_repo.update_size(UUID(client_id), new_size)

    except Exception as e:
        db.rollback()

        if "job" in locals() and job is not None:
            job.mark_failed(str(e))
            job_repo.update(job)
            db.commit()

            publish_job_event(
                "job_failed",
                {
                    "job_id": str(job.id),
                    "status": "failed",
                    "error": str(e),
                    "client_id": client_id,
                },
            )

        if (
            "output_path" in locals()
            and output_path is not None
            and output_path.exists()
        ):
            output_path.unlink(missing_ok=True)

        if "client_id" in locals() and client_id:
            client_dir = get_client_output_dir(client_id)
            new_size = get_directory_size(client_dir)
            storage_repo.update_size(UUID(client_id), new_size)

    finally:
        db.close()
