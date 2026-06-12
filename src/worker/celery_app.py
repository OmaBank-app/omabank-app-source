from celery import Celery

from src.core.config import settings

# Initialize Celery using the Redis broker URL
celery_instance = Celery(
    "omabank_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.worker.tasks"],
)

celery_instance.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # SRE Constraint: Limit worker concurrency to save RAM on B2s_v2
    worker_concurrency=2,
    task_track_started=True,
    task_time_limit=300,  # Kill tasks that hang longer than 5 minutes
)
