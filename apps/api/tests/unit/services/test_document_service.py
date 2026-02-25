from pathlib import Path
from uuid import uuid4

from app.domain.enums.conversion_type import ConversionType
from app.services.document_service import DocumentService


class DummyJobRepository:
    def __init__(self):
        self.saved_jobs = []

    def save(self, job):
        self.saved_jobs.append(job)


class DummyStorageRepository:
    pass


def test_create_job_saves_job_and_builds_expected_paths(tmp_path, monkeypatch):
    client_id = uuid4()
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    repo = DummyJobRepository()
    service = DocumentService(repo, DummyStorageRepository())

    monkeypatch.setattr(
        "app.services.document_service.get_client_input_dir",
        lambda _client_id: input_dir,
    )
    monkeypatch.setattr(
        "app.services.document_service.get_client_output_dir",
        lambda _client_id: output_dir,
    )

    job = service.create_job(client_id, ConversionType.CSV_TO_JSON, "sample.csv")

    assert input_dir.exists()
    assert output_dir.exists()
    assert len(repo.saved_jobs) == 1
    assert repo.saved_jobs[0] is job
    assert Path(job.input_path).parent == input_dir
    assert Path(job.input_path).name.endswith("_sample.csv")
    assert Path(job.output_path).parent == output_dir
    assert Path(job.output_path).suffix == ".json"


def test_create_job_uses_fallback_extension_for_unknown_conversion_type(
    tmp_path, monkeypatch
):
    client_id = uuid4()
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    repo = DummyJobRepository()
    service = DocumentService(repo, DummyStorageRepository())

    monkeypatch.setattr(
        "app.services.document_service.get_client_input_dir",
        lambda _client_id: input_dir,
    )
    monkeypatch.setattr(
        "app.services.document_service.get_client_output_dir",
        lambda _client_id: output_dir,
    )

    job = service.create_job(client_id, "custom_conversion", "file.bin")

    assert Path(job.output_path).suffix == ".out"
