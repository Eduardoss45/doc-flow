from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from pathlib import Path

from src.domain.enums import JobStatus, ConversionType

@dataclass
class DocumentJob:
    conversion_type: ConversionType
    input_filename: str
    input_path: str
    output_path: str | None = None
    status: JobStatus = JobStatus.PENDING
    error_message: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=2)
    )
    id: UUID = field(default_factory=uuid4)

    def mark_processing(self) -> None:
        self.status = JobStatus.PROCESSING
        self.updated_at = datetime.utcnow()

    def mark_completed(self, output_path: str) -> None:
        self.status = JobStatus.COMPLETED
        self.output_path = output_path
        self.expires_at = datetime.utcnow() + timedelta(hours=1)
        self.updated_at = datetime.utcnow()

    def mark_failed(self, error_message: str) -> None:
        self.status = JobStatus.FAILED
        self.error_message = error_message
        self.expires_at = datetime.utcnow() + timedelta(minutes=10)
        self.updated_at = datetime.utcnow()

@property
def is_expired(self) -> bool:
    return self.expires_at is not None and datetime.utcnow() > self.expires_at