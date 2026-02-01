from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.enums.job_status import JobStatus
from src.domain.enums.conversion_type import ConversionType


@dataclass
class DocumentJob:
    conversion_type: ConversionType
    input_path: str
    output_path: str | None = None
    status: JobStatus = JobStatus.PENDING
    error_message: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def mark_processing(self) -> None:
        self.status = JobStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def mark_completed(self, output_path: str) -> None:
        self.status = JobStatus.COMPLETED
        self.output_path = output_path
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error_message: str) -> None:
        self.status = JobStatus.FAILED
        self.error_message = error_message
        self.updated_at = datetime.utcnow()
