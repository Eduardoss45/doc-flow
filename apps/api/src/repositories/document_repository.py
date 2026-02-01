from typing import Dict
from uuid import UUID

from src.domain.entities import DocumentJob


class DocumentRepository:
    """
    Repository temporário em memória.
    Será substituído por PostgreSQL futuramente.
    """

    def __init__(self):
        self._store: Dict[UUID, DocumentJob] = {}

    def save(self, job: DocumentJob) -> None:
        self._store[job.id] = job

    def get_by_id(self, job_id: UUID) -> DocumentJob | None:
        return self._store.get(job_id)
