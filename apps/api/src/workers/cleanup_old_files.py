from celery import shared_task
from pathlib import Path
from datetime import datetime, timedelta
from uuid import UUID
from infrastructure.db.db import SessionLocal
from src.repositories.client_storage_repository import ClientStorageRepository
from infrastructure.models.client_storage_model import ClientStorageModel
from src.infrastructure.storage.utils import get_client_input_dir, get_client_output_dir


@shared_task
def cleanup_expired_files():
    db = SessionLocal()
    try:
        storage_repo = ClientStorageRepository(db)
        now = datetime.utcnow()

        expired_storages = (
            db.query(ClientStorageModel)
            .filter(ClientStorageModel.expires_at < now)
            .all()
        )

        for storage_model in expired_storages:
            cid = str(storage_model.client_id)

            input_dir = get_client_input_dir(cid)
            output_dir = get_client_output_dir(cid)

            if input_dir.exists():
                import shutil

                shutil.rmtree(input_dir, ignore_errors=True)

            if output_dir.exists():
                shutil.rmtree(output_dir, ignore_errors=True)

            db.delete(storage_model)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
