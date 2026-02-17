from sqlalchemy import Column, String, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.infra.db.db import Base
import uuid
from datetime import datetime


class ClientStorageModel(Base):
    __tablename__ = "client_storages"

    client_id = Column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    size_bytes = Column(BigInteger, default=0, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_calculated_at = Column(DateTime, nullable=True)
