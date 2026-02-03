from src.infrastructure.database import SessionLocal
from celery import shared_task
from pathlib import Path
from datetime import datetime, timedelta
from src.repositories.document_repository import DocumentRepository


@shared_task
def cleanup_expired_files():
    db = SessionLocal()
    try:
        repo = DocumentRepository(db)
        output_dir = Path("src/infrastructure/storage/output")

        for file_path in output_dir.glob("*"):
            if not file_path.is_file():
                continue

            job_id = file_path.stem.split("_")[0]

            job = repo.get_by_id(job_id)

            if job and job.is_expired:
                file_path.unlink(missing_ok=True)
                print(f"Removido (job expirado): {file_path}")
            else:
                # fallback por tempo de arquivo
                age = datetime.utcnow() - datetime.fromtimestamp(file_path.stat().st_mtime)
                if age > timedelta(hours=2):
                    file_path.unlink(missing_ok=True)
                    print(f"Removido (fallback): {file_path}")

    finally:
        db.close()
