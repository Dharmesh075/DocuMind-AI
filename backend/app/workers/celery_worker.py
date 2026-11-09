"""
DocuMind AI - Celery Background Worker
Processes computationally heavy document OCR, layout analysis, and ML pipelines.
"""

from celery import Celery
from app.core.config import settings
from app.database.session import SessionLocal
from app.services.document_service import process_document_pipeline

celery_app = Celery(
    "documind_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True
)

@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: str):
    db = SessionLocal()
    try:
        doc = process_document_pipeline(document_id, db)
        return {
            "status": "success",
            "document_id": doc.id,
            "document_type": doc.document_type,
            "confidence": doc.confidence_score
        }
    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=5)
    finally:
        db.close()
