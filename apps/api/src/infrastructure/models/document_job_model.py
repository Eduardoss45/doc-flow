
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from infrastructure.db.db import Base
from src.domain.enums import JobStatus, ConversionType
import uuid
from datetime import datetime

class DocumentJobModel(Base):
    __tablename__ = "document_jobs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversion_type = Column(Enum(ConversionType), nullable=False)
    input_filename = Column(String, nullable=False)
    input_path = Column(String, nullable=False)
    output_path = Column(String)
    status = Column(Enum(JobStatus), nullable=False)
    error_message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
