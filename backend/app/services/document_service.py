"""
DocuMind AI - Document Processing Orchestrator
Coordinates the 7 pipeline modules for end-to-end processing.
"""

import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.document import Document, ProcessingJob, ExtractedField, ExtractionRun, AuditLog
from app.pipelines.preprocessing import generate_document_preview
from app.pipelines.ocr_engine import run_ocr
from app.pipelines.classifier import classify_document
from app.pipelines.extractor import extract_information
from app.pipelines.validator import validate_extracted_fields
from app.pipelines.confidence import compute_field_confidence, compute_document_confidence

def process_document_pipeline(document_id: str, db: Session) -> Document:
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise ValueError(f"Document {document_id} not found.")

    job = db.query(ProcessingJob).filter(ProcessingJob.document_id == document_id).order_by(ProcessingJob.started_at.desc()).first()
    if job:
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        db.commit()

    try:
        # Step 1: Preprocessing & Preview Rendering
        document.status = "preprocessing"
        db.commit()
        preview_path = generate_document_preview(document.storage_path, document.id)
        document.preview_image_path = preview_path

        # Step 2: OCR & Layout Analysis
        document.status = "ocr"
        db.commit()
        ocr_result = run_ocr(document.storage_path)
        ocr_text = ocr_result.get("text", "")
        ocr_blocks = ocr_result.get("blocks", [])
        page_count = ocr_result.get("page_count", 1)

        document.raw_ocr_text = ocr_text
        document.page_count = page_count

        # Step 3: Document Classification (Scikit-Learn TF-IDF + Logistic Regression)
        document.status = "classifying"
        db.commit()
        class_res = classify_document(ocr_text)
        document.document_type = class_res["document_type"]

        # Step 4: Intelligent Information Extraction
        document.status = "extracting"
        db.commit()
        extraction_res = extract_information(document.document_type, ocr_text, ocr_blocks)
        extracted_fields_raw = extraction_res.get("fields", [])
        structured_data = extraction_res.get("structured_data", {})

        # Step 5: Validation & Consistency Checking
        document.status = "validating"
        db.commit()
        validated_fields, doc_alerts = validate_extracted_fields(
            document.document_type, extracted_fields_raw, structured_data
        )

        # Step 6: Confidence Scoring
        for f in validated_fields:
            f["confidence"] = compute_field_confidence(f)

        overall_conf = compute_document_confidence(validated_fields, doc_alerts)
        document.confidence_score = overall_conf

        # Step 7: Persist Extracted Fields to Database
        # Clean previous fields if reprocessing
        db.query(ExtractedField).filter(ExtractedField.document_id == document.id).delete()

        for f in validated_fields:
            db_field = ExtractedField(
                document_id=document.id,
                field_name=f["field_name"],
                field_value=f.get("field_value"),
                confidence=f.get("confidence", 1.0),
                page_number=1,
                bounding_box=f.get("bounding_box"),
                is_verified=False,
                validation_status=f.get("validation_status", "valid"),
                warning_message=f.get("warning_message")
            )
            db.add(db_field)

        # Record Extraction Run
        run = ExtractionRun(
            document_id=document.id,
            model_name="tfidf-logistic-regression + pattern-extractor",
            model_version="1.0.0",
            raw_result=structured_data,
            validated_result={"fields": validated_fields, "alerts": doc_alerts}
        )
        db.add(run)

        # Final Status
        if len(doc_alerts) > 0 or overall_conf < 0.85:
            document.status = "needs_review"
        else:
            document.status = "extracted"

        if job:
            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(document)
        return document

    except Exception as e:
        db.rollback()
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
        document.status = "failed"
        db.commit()
        raise e
