"""
DocuMind AI - Processing Jobs Route
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.document import ProcessingJob
from app.schemas.document import JobStatusResponse

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job:
        # Also check by document_id in case document_id was passed
        job = db.query(ProcessingJob).filter(ProcessingJob.document_id == job_id).order_by(ProcessingJob.started_at.desc()).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.id,
        document_id=job.document_id,
        status=job.status,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message
    )
