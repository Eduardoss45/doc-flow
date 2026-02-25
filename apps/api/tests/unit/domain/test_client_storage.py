from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.domain.entities.client_storage import ClientStorage, MAX_DAILY_QUOTA_BYTES


def test_create_new_sets_expected_initial_values():
    client_id = uuid4()

    storage = ClientStorage.create_new(client_id)

    assert storage.client_id == client_id
    assert storage.size_bytes == 0
    assert storage.last_calculated_at is None
    assert storage.expires_at > storage.created_at


def test_can_upload_returns_false_when_expired():
    storage = ClientStorage(
        client_id=uuid4(),
        size_bytes=0,
        created_at=datetime.now(timezone.utc) - timedelta(days=2),
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )

    allowed, message = storage.can_upload(1024)

    assert allowed is False
    assert "expirada" in message.lower()


def test_can_upload_returns_false_when_quota_would_be_exceeded():
    storage = ClientStorage(
        client_id=uuid4(),
        size_bytes=MAX_DAILY_QUOTA_BYTES - 100,
    )

    allowed, message = storage.can_upload(101)

    assert allowed is False
    assert "cota" in message.lower()


def test_can_upload_returns_true_when_within_quota():
    storage = ClientStorage(
        client_id=uuid4(),
        size_bytes=1024,
    )

    allowed, message = storage.can_upload(1024)

    assert allowed is True
    assert message == ""
