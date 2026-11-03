import io
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.factory import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_upload_enqueues_process_conversion(client):
    client_id = str(uuid4())
    client.set_cookie("client_id", client_id)

    csv_bytes = b"name,age\nAlice,30\n"
    data = {
        "conversion_type": "csv_to_json",
        "file": (io.BytesIO(csv_bytes), "sample.csv"),
    }

    with patch.object(
        client.application.extensions["celery"],
        "send_task",
    ) as mock_send:
        response = client.post(
            "/documents/upload",
            data=data,
            content_type="multipart/form-data",
        )

    assert response.status_code == 202
    body = response.get_json()
    assert "job_id" in body
    assert body["status"]
    assert (
        "enfileirado" in body["message"].lower()
        or "processamento" in body["message"].lower()
    )

    mock_send.assert_called_once()
    args, kwargs = mock_send.call_args
    assert args[0] == "process_conversion"
    task_args = kwargs.get("args") or (args[1] if len(args) > 1 else None)
    call_kwargs = mock_send.call_args
    assert call_kwargs.kwargs.get("args")[0] == body["job_id"]
    assert call_kwargs.kwargs.get("args")[1] == client_id
