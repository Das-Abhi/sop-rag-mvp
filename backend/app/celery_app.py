"""
Celery application configuration and initialization
"""
from celery import Celery
from celery.schedules import crontab
import os
from loguru import logger

# Initialize Celery app
app = Celery(
    "sop_rag_mvp",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

# Configure Celery
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minute hard limit
    task_soft_time_limit=25 * 60,  # 25 minute soft limit
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
)

# Configure periodic tasks (optional)
app.conf.beat_schedule = {
    "cleanup-old-tasks": {
        "task": "app.tasks.document_tasks.cleanup_old_results",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}

# Auto-discover tasks from task modules
app.autodiscover_tasks(["app.tasks"])

logger.info("Celery app configured")
