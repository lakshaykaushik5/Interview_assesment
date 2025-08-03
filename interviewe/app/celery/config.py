from celery import Celery

from dotenv import load_dotenv,find_dotenv
import os 

load_dotenv(find_dotenv())


celery_app = Celery(
    "interview_service",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_BACKEND_URL"),
    include=["app.celery_app.tasks"]
)


celery_app.conf.update(
    task_serializer ="json",
    accept_content = ["json"],
    result_serializer = "json",
    timezone = "UTC",
    enable_utc = True,
    task_track_started=True,
    task_time_limit=30*60, # 30 minutes
    task_soft_time_limit = 25*60, #25 minutes
    worker_prefetch_multiplier=1,
    worker_max_task_per_child = 1000
)



celery_app.conf.task_routes = {
    "app.celery_app.tasks.process_question_generation": {"queue": "question_generation"},
    "app.celery_app.tasks.process_response_evaluation": {"queue": "evaluation"},
    "app.celery_app.tasks.process_memory_retrieval": {"queue": "memory"},
    "app.celery_app.tasks.process_follow_up": {"queue": "follow_up"},
}
