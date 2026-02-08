from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone
from src.domain.entities.client_storage import ClientStorage
from infrastructure.models.client_storage_model import ClientStorageModel
from src.infrastructure.storage.utils import get_directory_size, get_client_output_dir


class ClientStorageRepository:

    def __init__(self, db: Session):
        self.db = db

    def save(self, storage: ClientStorage) -> None:
        model = self._get_or_create_model(storage.client_id)

        model.size_bytes = storage.size_bytes
        model.created_at = storage.created_at
        model.expires_at = storage.expires_at
        model.last_calculated_at = storage.last_calculated_at

        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

    def update_size(self, client_id: UUID, new_size_bytes: int) -> None:
        model = self._get_model(client_id)
        if not model:
            return

        model.size_bytes = new_size_bytes
        model.last_calculated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(model)

    def get_by_client_id(self, client_id: UUID | str) -> ClientStorage | None:
        if isinstance(client_id, str):
            try:
                client_id = UUID(client_id)
            except ValueError:
                return None

        model = self.db.query(ClientStorageModel).filter_by(client_id=client_id).first()
        if not model:
            return None

        return self._to_domain(model)

    def get_or_create(self, client_id: UUID) -> ClientStorage:
        storage = self.get_by_client_id(client_id)
        if storage:
            return storage

        new_storage = ClientStorage.create_new(client_id)
        self.save(new_storage)
        return new_storage

    def _get_model(self, client_id: UUID) -> ClientStorageModel | None:
        return self.db.query(ClientStorageModel).filter_by(client_id=client_id).first()

    def _get_or_create_model(self, client_id: UUID) -> ClientStorageModel:
        model = self._get_model(client_id)
        if model:
            return model

        model = ClientStorageModel(client_id=client_id)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def _to_domain(self, model: ClientStorageModel) -> ClientStorage:
        return ClientStorage(
            client_id=model.client_id,
            size_bytes=model.size_bytes or 0,
            created_at=(
                model.created_at.astimezone(timezone.utc) if model.created_at else None
            ),
            expires_at=(
                model.expires_at.astimezone(timezone.utc) if model.expires_at else None
            ),
            last_calculated_at=(
                model.last_calculated_at.astimezone(timezone.utc)
                if model.last_calculated_at
                else None
            ),
        )
