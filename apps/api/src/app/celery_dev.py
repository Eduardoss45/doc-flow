import threading
import subprocess
import sys
import os


def start_celery_worker():
    subprocess.call([
        sys.executable,
        "-m",
        "celery",
        "-A",
        "src.app.main.celery",
        "worker",
        "--loglevel=info",
        "--pool=solo",  
    ])


def start_celery_beat():
    subprocess.call([
        sys.executable,
        "-m",
        "celery",
        "-A",
        "src.app.main.celery",
        "beat",
        "--loglevel=info",
    ])


def start_celery_dev():
    worker_thread = threading.Thread(
        target=start_celery_worker,
        daemon=True,
    )

    beat_thread = threading.Thread(
        target=start_celery_beat,
        daemon=True,
    )

    worker_thread.start()
    beat_thread.start()
