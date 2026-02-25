from datetime import timedelta

from app.domain.entities.document_job import DocumentJob
from app.domain.enums.conversion_type import ConversionType
from app.domain.enums.job_status import JobStatus


def test_mark_processing_updates_status():
    job = DocumentJob(
        conversion_type=ConversionType.CSV_TO_JSON,
        input_filename="input.csv",
        input_path="/tmp/input.csv",
    )
    previous_updated_at = job.updated_at

    job.mark_processing()

    assert job.status == JobStatus.PROCESSING
    assert job.updated_at >= previous_updated_at


def test_mark_completed_sets_output_and_extends_expiration():
    job = DocumentJob(
        conversion_type=ConversionType.CSV_TO_JSON,
        input_filename="input.csv",
        input_path="/tmp/input.csv",
    )
    previous_expires_at = job.expires_at

    job.mark_completed("/tmp/output.json")

    assert job.status == JobStatus.COMPLETED
    assert job.output_path == "/tmp/output.json"
    assert job.expires_at > previous_expires_at - timedelta(seconds=1)


def test_mark_failed_sets_error_and_short_expiration():
    job = DocumentJob(
        conversion_type=ConversionType.CSV_TO_JSON,
        input_filename="input.csv",
        input_path="/tmp/input.csv",
    )

    job.mark_failed("conversion error")

    assert job.status == JobStatus.FAILED
    assert job.error_message == "conversion error"
