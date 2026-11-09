"""
DocuMind AI - REST API Routes: Documents, Processing, Review, Export
"""

import io
import csv
import json
import base64
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Request, BackgroundTasks, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.document import Document, ProcessingJob, ExtractedField, AuditLog, ExtractionRun, generate_doc_id
from app.schemas.document import (
    DocumentUploadResponse, DocumentSummary, DocumentDetail,
    ExtractedFieldItem, ExtractedFieldUpdate, AuditLogItem,
    JobStatusResponse, AnalyticsResponse
)
from app.core.config import settings
from app.pipelines.ingestion import compute_sha256
from app.services.document_service import process_document_pipeline

router = APIRouter(prefix="/documents", tags=["Documents"])

def parse_multipart_body(raw_body: bytes, content_type: str) -> tuple[str, str, bytes]:
    """Pure-Python standard parser for multipart/form-data without external dependency."""
    m = re.search(r'boundary=([^\s;]+)', content_type)
    if not m:
        return "uploaded_file.bin", "application/octet-stream", raw_body

    boundary = m.group(1).encode()
    parts = raw_body.split(b'--' + boundary)
    for part in parts:
        if b'Content-Disposition:' in part and b'filename=' in part:
            headers_part, _, file_data = part.partition(b'\r\n\r\n')
            file_data = file_data.rstrip(b'\r\n--')
            
            fn_match = re.search(r'filename="([^"]+)"', headers_part.decode('latin1', errors='ignore'))
            filename = fn_match.group(1) if fn_match else "uploaded_document"

            ct_match = re.search(r'Content-Type:\s*([^\r\n]+)', headers_part.decode('latin1', errors='ignore'))
            ct = ct_match.group(1).strip() if ct_match else "application/octet-stream"

            return filename, ct, file_data

    return "uploaded_file.bin", "application/octet-stream", raw_body

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    auto_process: bool = Query(True, description="Automatically trigger processing pipeline after upload"),
    db: Session = Depends(get_db)
):
    """Uploads a new document via multipart/form-data, raw bytes, or base64 JSON."""
    content_type = request.headers.get("content-type", "")
    filename = request.query_params.get("filename", "uploaded_document.pdf")
    file_type = "application/pdf"
    file_bytes = b""

    if "application/json" in content_type:
        body = await request.json()
        filename = body.get("filename", filename)
        file_type = body.get("file_type", file_type)
        if "content_base64" in body and body["content_base64"]:
            file_bytes = base64.b64decode(body["content_base64"])
        elif "raw_text" in body and body["raw_text"]:
            file_bytes = body["raw_text"].encode("utf-8")
        else:
            raise HTTPException(status_code=400, detail="Missing content_base64 or raw_text in JSON payload")
    elif "multipart/form-data" in content_type:
        raw_body = await request.body()
        filename, file_type, file_bytes = parse_multipart_body(raw_body, content_type)
    else:
        file_bytes = await request.body()
        file_type = content_type or "application/octet-stream"

    # Validation
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS and ext != "":
        if not ext:
            ext = ".pdf"
            filename += ext
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )

    file_size = len(file_bytes)
    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    file_hash = compute_sha256(file_bytes)
    existing_doc = db.query(Document).filter(Document.file_hash == file_hash).first()
    is_duplicate = existing_doc is not None

    doc_id = generate_doc_id()
    safe_filename = f"{doc_id}_{Path(filename).name}"
    storage_path = settings.STORAGE_DIR / safe_filename

    with open(storage_path, "wb") as f:
        f.write(file_bytes)

    doc = Document(
        id=doc_id,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
        file_hash=file_hash,
        storage_path=str(storage_path),
        status="uploaded"
    )
    db.add(doc)

    job = ProcessingJob(
        document_id=doc_id,
        status="queued",
        started_at=datetime.utcnow()
    )
    db.add(job)
    db.commit()
    db.refresh(doc)

    if auto_process:
        background_tasks.add_task(process_document_pipeline, doc.id, db)

    return DocumentUploadResponse(
        document_id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        status="processing" if auto_process else doc.status,
        is_duplicate=is_duplicate,
        message="Document uploaded and processing queued." if auto_process else "Document uploaded successfully."
    )

@router.get("", response_model=list[DocumentSummary])
def get_documents(
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Retrieves all documents with optional filtering and pagination."""
    query = db.query(Document)
    if status:
        query = query.filter(Document.status == status)
    if document_type:
        query = query.filter(Document.document_type == document_type)
    if search:
        query = query.filter(Document.filename.ilike(f"%{search}%"))

    docs = query.order_by(Document.uploaded_at.desc()).offset(skip).limit(limit).all()
    return docs

@router.get("/{document_id}", response_model=DocumentDetail)
def get_document_details(document_id: str, db: Session = Depends(get_db)):
    """Retrieves document detail, bounding boxes, and audit history."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    fields = db.query(ExtractedField).filter(ExtractedField.document_id == document_id).all()
    logs = db.query(AuditLog).filter(AuditLog.document_id == document_id).order_by(AuditLog.modified_at.desc()).all()
    latest_run = db.query(ExtractionRun).filter(ExtractionRun.document_id == document_id).order_by(ExtractionRun.created_at.desc()).first()

    preview_url = f"/api/v1/documents/{document_id}/preview" if doc.preview_image_path else None

    return DocumentDetail(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        document_type=doc.document_type,
        status=doc.status,
        confidence_score=doc.confidence_score,
        page_count=doc.page_count,
        uploaded_at=doc.uploaded_at,
        updated_at=doc.updated_at,
        raw_ocr_text=doc.raw_ocr_text,
        preview_url=preview_url,
        fields=[
            ExtractedFieldItem(
                id=f.id,
                field_name=f.field_name,
                field_value=f.field_value,
                confidence=f.confidence,
                page_number=f.page_number,
                bounding_box=f.bounding_box,
                is_verified=f.is_verified,
                validation_status=f.validation_status,
                warning_message=f.warning_message
            ) for f in fields
        ],
        audit_logs=[
            AuditLogItem(
                id=l.id,
                field_id=l.field_id,
                field_name=l.field_name,
                old_value=l.old_value,
                new_value=l.new_value,
                modified_by=l.modified_by,
                modified_at=l.modified_at
            ) for l in logs
        ],
        structured_data=latest_run.raw_result if latest_run else None
    )

@router.get("/{document_id}/preview")
def get_document_preview(document_id: str, db: Session = Depends(get_db)):
    """Serves the generated high-resolution page preview image."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc or not doc.preview_image_path or not Path(doc.preview_image_path).exists():
        raise HTTPException(status_code=404, detail="Preview image not available")
    return FileResponse(doc.preview_image_path, media_type="image/png")

@router.post("/{document_id}/process")
def trigger_process_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Triggers document processing pipeline."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    background_tasks.add_task(process_document_pipeline, document_id, db)
    return {"status": "processing_started", "document_id": document_id}

@router.get("/{document_id}/results")
def get_document_results(document_id: str, db: Session = Depends(get_db)):
    """Returns pure structured JSON extraction results."""
    run = db.query(ExtractionRun).filter(ExtractionRun.document_id == document_id).order_by(ExtractionRun.created_at.desc()).first()
    if not run:
        raise HTTPException(status_code=404, detail="No extraction results found for this document")
    return {
        "document_id": document_id,
        "model": run.model_name,
        "extracted_data": run.raw_result,
        "validation": run.validated_result
    }

@router.patch("/{document_id}/fields/{field_id}")
def update_extracted_field(
    document_id: str,
    field_id: str,
    payload: ExtractedFieldUpdate,
    db: Session = Depends(get_db)
):
    """Human-in-the-Loop: Edits an extracted field and records an audit log entry."""
    field = db.query(ExtractedField).filter(
        ExtractedField.id == field_id,
        ExtractedField.document_id == document_id
    ).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    old_val = field.field_value
    field.field_value = payload.field_value
    field.is_verified = True
    field.validation_status = "valid"
    field.warning_message = "Manually verified by human operator"
    field.confidence = 1.0

    audit_entry = AuditLog(
        document_id=document_id,
        field_id=field_id,
        field_name=field.field_name,
        old_value=old_val,
        new_value=payload.field_value,
        modified_by=payload.modified_by or "human_operator",
        modified_at=datetime.utcnow()
    )
    db.add(audit_entry)

    doc = db.query(Document).filter(Document.id == document_id).first()
    if doc:
        doc.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(field)

    return {
        "status": "updated",
        "field_id": field.id,
        "field_name": field.field_name,
        "new_value": field.field_value,
        "confidence": field.confidence
    }

@router.post("/{document_id}/approve")
def approve_document(document_id: str, db: Session = Depends(get_db)):
    """Human-in-the-Loop: Approves the document after review."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    doc.status = "approved"
    doc.updated_at = datetime.utcnow()
    db.query(ExtractedField).filter(ExtractedField.document_id == document_id).update({"is_verified": True})
    db.commit()

    return {"status": "approved", "document_id": document_id}

@router.post("/{document_id}/reprocess")
def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Re-runs the entire pipeline for the document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    background_tasks.add_task(process_document_pipeline, document_id, db)
    return {"status": "reprocessing_queued", "document_id": document_id}

@router.get("/{document_id}/export")
def export_document_data(
    document_id: str,
    format: str = Query("json", enum=["json", "csv"]),
    db: Session = Depends(get_db)
):
    """Exports structured document data as JSON or CSV."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    fields = db.query(ExtractedField).filter(ExtractedField.document_id == document_id).all()
    data_dict = {f.field_name: f.field_value for f in fields}

    if format == "json":
        export_payload = {
            "document_id": doc.id,
            "filename": doc.filename,
            "document_type": doc.document_type,
            "confidence_score": doc.confidence_score,
            "status": doc.status,
            "data": data_dict
        }
        return JSONResponse(
            content=export_payload,
            headers={"Content-Disposition": f"attachment; filename={doc.id}_export.json"}
        )
    else:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Field Name", "Extracted Value", "Confidence", "Status"])
        for f in fields:
            writer.writerow([f.field_name, f.field_value or "", f"{f.confidence*100:.1f}%", f.validation_status])

        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={doc.id}_export.csv"}
        )

@router.post("/sample/{sample_type}")
def create_sample_document(
    sample_type: str,
    db: Session = Depends(get_db)
):
    """Creates and processes a realistic sample document for instant testing."""
    sample_texts = {
        "invoice": "TAX INVOICE ABC Technologies Pvt Ltd\nInvoice Number: INV-1024\nDate: 09/11/2026\nDue Date: 24/11/2026\nBill To: Acme Corp\nGSTIN: 29ABCDE1234F1Z5\nItem Description: Cloud Architecture Consulting Qty: 40 Rate: 250 Amount: 10000\nSubtotal: 10000.00\nTax (SGST+CGST 18%): 1800.00\nTotal Amount: 11800.00\nPayment Terms: Net 15 days Bank Details: HDFC Bank",
        "receipt": "STARBUCKS COFFEE STORE #14092\n104 MARKET ST SAN FRANCISCO CA\nDATE: 11/08/2026 08:42 AM\nCaffe Latte Grande $5.25\nBlueberry Scone $3.95\nSubtotal: $9.20\nTax: $0.78\nTOTAL: $9.98\nPAYMENT METHOD: VISA CONTACTLESS\nAUTH: 084920 THANKS FOR VISITING",
        "resume": "ALEXANDER CHEN\nSenior Full Stack & AI Engineer\nEmail: alex.chen@example.com | Phone: +1-555-019-2834 | San Francisco, CA\nSUMMARY: Experienced software engineer specializing in Next.js, Python, FastAPI, and machine learning document processing pipelines.\nSKILLS: Python, TypeScript, Next.js, React, FastAPI, Scikit-learn, PyTorch, Docker, PostgreSQL\nEXPERIENCE: Lead ML Engineer at DataStream Inc\nEDUCATION: B.S. in Computer Science - UC Berkeley",
        "application_form": "APPLICATION FOR EMPLOYMENT\nCandidate Application Form\nPosition Applied For: Senior Backend Engineer\nApplicant Full Name: Robert Michael Taylor\nDate of Birth: 14/05/1992\nSocial Security Number / ID: XXX-XX-4819\nResidential Address: 742 Evergreen Terrace, Springfield, OR\nContact Phone: (555) 321-7654\nSignature: R. Taylor Date: 09/11/2026"
    }

    if sample_type not in sample_texts:
        raise HTTPException(status_code=400, detail=f"Invalid sample type '{sample_type}'. Valid: {list(sample_texts.keys())}")

    doc_id = generate_doc_id()
    filename = f"sample_{sample_type}_{doc_id[-6:]}.txt"
    file_path = settings.STORAGE_DIR / filename
    text_content = sample_texts[sample_type]

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text_content)

    doc = Document(
        id=doc_id,
        filename=filename,
        file_type="text/plain",
        file_size=len(text_content.encode()),
        file_hash=f"sample_hash_{doc_id}",
        storage_path=str(file_path),
        status="uploaded"
    )
    db.add(doc)
    job = ProcessingJob(document_id=doc_id, status="queued")
    db.add(job)
    db.commit()

    # Process immediately
    process_document_pipeline(doc_id, db)

    return {"status": "created_and_processed", "document_id": doc_id, "sample_type": sample_type}
