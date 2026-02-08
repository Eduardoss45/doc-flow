from celery import shared_task
from pathlib import Path
from datetime import datetime, timedelta
from uuid import UUID
from infrastructure.db.db import SessionLocal
from src.repositories.document_repository import DocumentRepository
from infrastructure.models.document_job_model import DocumentJobModel


@shared_task
def cleanup_expired_files():
    db = SessionLocal()
    try:
        repo = DocumentRepository(db)
        now = datetime.utcnow()

        output_dir = Path("src/infrastructure/storage/output").resolve()
        if not output_dir.exists() or not output_dir.is_dir():
            return

        # 1. Remove jobs expirados (banco → filesystem)
        expired_jobs = repo.get_expired_jobs()

        for job in expired_jobs:
            if job.output_path:
                Path(job.output_path).unlink(missing_ok=True)

            repo.delete(job.id)

        db.commit()

        # 2. Remove arquivos órfãos antigos
        for file_path in output_dir.iterdir():
            if not file_path.is_file():
                continue

            try:
                uuid_str = file_path.stem.split("_", 1)[0]
                UUID(uuid_str)
            except Exception:
                age = now - datetime.fromtimestamp(file_path.stat().st_mtime)
                if age > timedelta(hours=24):
                    file_path.unlink(missing_ok=True)
                continue

            if not repo.get_by_id(uuid_str):
                age = now - datetime.fromtimestamp(file_path.stat().st_mtime)
                if age > timedelta(hours=24):
                    file_path.unlink(missing_ok=True)

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
