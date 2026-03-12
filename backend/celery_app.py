from celery import Celery
from backend.core.config import settings

celery_app = Celery(
    "ai_code_quality",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["backend.tasks.code_review_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=270,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)
