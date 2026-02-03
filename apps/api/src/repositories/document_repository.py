from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID

from src.domain.entities.document_job import DocumentJob
from src.infrastructure.models.document_job_model import DocumentJobModel


class DocumentRepository:

    def __init__(self, db: Session):
        self.db = db

    def save(self, job: DocumentJob) -> None:
        model = DocumentJobModel(
            id=job.id,
            conversion_type=job.conversion_type,
            input_filename=job.input_filename,
            input_path=job.input_path,
            output_path=job.output_path,
            status=job.status,
            error_message=job.error_message,
            created_at=job.created_at,
            updated_at=job.updated_at,
            expires_at=job.expires_at,
        )

        self.db.add(model)
        self.db.commit()

    def get_by_id(self, job_id: UUID) -> DocumentJob | None:
        model = (
            self.db
            .query(DocumentJobModel)
            .filter_by(id=job_id)
            .first()
        )

        if not model:
            return None

        return self._to_domain(model)

    def get_expired_jobs(self) -> list[DocumentJob]:
        models = (
            self.db
            .query(DocumentJobModel)
            .filter(DocumentJobModel.expires_at < datetime.utcnow())
            .all()
        )

        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: DocumentJobModel) -> DocumentJob:
        return DocumentJob(
            id=model.id,
            conversion_type=model.conversion_type,
            input_filename=model.input_filename,
            input_path=model.input_path,
            output_path=model.output_path,
            status=model.status,
            error_message=model.error_message,
            created_at=model.created_at,
            updated_at=model.updated_at,
            expires_at=model.expires_at,
        )


