from celery import Celery
from celery.schedules import crontab
from src.app.config import config

celery = Celery(
    "document_processor",
    broker=config.RABBITMQ_URL,
    backend=config.REDIS_URL,
    include=[
        "src.workers.tasks.conversion_worker",
        "src.workers.tasks.cleanup_old_files",
    ],
)

celery.conf.update(
    timezone=config.TIMEZONE,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

celery.conf.beat_schedule = {
    "cleanup-expired-job": {
        "task": "src.workers.tasks.cleanup_old_files.cleanup_expired_files",
        "schedule": crontab(minute="*/1"),
    },
}
