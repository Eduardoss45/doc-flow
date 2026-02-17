from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from pathlib import Path
from typing import Optional


MAX_DAILY_QUOTA_BYTES = 250 * 1024 * 1024


@dataclass
class ClientStorage:
    client_id: UUID
    size_bytes: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24 * 7)
    )
    last_calculated_at: Optional[datetime] = None

    @classmethod
    def create_new(cls, client_id: UUID) -> "ClientStorage":
        now = datetime.now(timezone.utc)
        return cls(
            client_id=client_id,
            size_bytes=0,
            created_at=now,
            expires_at=now + timedelta(hours=24),
            last_calculated_at=None,
        )

    @property
    def is_expired(self) -> bool:
        now_utc = datetime.now(timezone.utc)
        if self.expires_at.tzinfo is None:
            expires_utc = self.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_utc = self.expires_at.astimezone(timezone.utc)
        return now_utc > expires_utc

    @property
    def remaining_bytes(self) -> int:
        return max(0, MAX_DAILY_QUOTA_BYTES - self.size_bytes)

    @property
    def used_mb(self) -> float:
        return self.size_bytes / (1024 * 1024)

    @property
    def quota_mb(self) -> int:
        return MAX_DAILY_QUOTA_BYTES // (1024 * 1024)

    def can_upload(self, file_size_bytes: int) -> tuple[bool, str]:
        if self.is_expired:
            return False, "Sessão expirada. Por favor, recarregue a página."
        if self.size_bytes + file_size_bytes > MAX_DAILY_QUOTA_BYTES:
            return False, (
                f"Limite de cota diária atingido ({self.quota_mb} MB). "
                f"Espaço usado: {self.used_mb:.1f} MB. "
                f"Faltam {self.remaining_bytes / (1024 * 1024):.1f} MB."
            )
        return True, ""

    def __post_init__(self):
        if isinstance(self.client_id, str):
            self.client_id = UUID(self.client_id)
