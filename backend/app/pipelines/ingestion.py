"""
DocuMind AI - Module 1: Document Ingestion
Responsible for:
- Validating extension and MIME type
- Calculating SHA-256 hash for duplicate detection
- Secure file storage
- Initializing Document and ProcessingJob records
"""

import os
import hashlib
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.document import Document, ProcessingJob, generate_doc_id

def compute_sha256(file_bytes: bytes) -> str:
    hasher = hashlib.sha256()
    hasher.update(file_bytes)
    return hasher.hexdigest()

def ingest_document(file: UploadFile, file_bytes: bytes, db: Session) -> tuple[Document, ProcessingJob, bool]:
    # 1. Validate file extension
    ext = Path(file.filename or "unknown").suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # 2. Check file size
    file_size = len(file_bytes)
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB}MB."
        )

    # 3. Calculate SHA-256
    file_hash = compute_sha256(file_bytes)

    # 4. Check for duplicates
    existing_doc = db.query(Document).filter(Document.file_hash == file_hash).first()
    is_duplicate = existing_doc is not None

    # 5. Generate unique Document ID
    doc_id = generate_doc_id()
    safe_filename = f"{doc_id}_{Path(file.filename or 'document').name}"
    storage_path = settings.STORAGE_DIR / safe_filename

    # 6. Save original file
    with open(storage_path, "wb") as f:
        f.write(file_bytes)

    # 7. Create Document record
    document = Document(
        id=doc_id,
        filename=file.filename or "document",
        file_type=file.content_type or f"application/{ext.replace('.', '')}",
        file_size=file_size,
        file_hash=file_hash,
        storage_path=str(storage_path),
        status="uploaded"
    )
    db.add(document)

    # 8. Create ProcessingJob record
    job = ProcessingJob(
        document_id=doc_id,
        status="queued",
        started_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    db.refresh(document)
    db.refresh(job)

    return document, job, is_duplicate
