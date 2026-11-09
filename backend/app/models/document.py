"""
DocuMind AI - SQLAlchemy Database Models
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database.session import Base

def utc_now():
    return datetime.now(timezone.utc)

def generate_doc_id():
    now_str = utc_now().strftime("%Y%m%d")
    short_uuid = uuid.uuid4().hex[:6].upper()
    return f"DOC-{now_str}-{short_uuid}"

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(128), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(64), primary_key=True, default=generate_doc_id)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(64), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)  # SHA-256 for duplicate check
    storage_path = Column(String(512), nullable=False)
    preview_image_path = Column(String(512), nullable=True)
    
    # Classification: invoice, receipt, resume, application_form, unknown
    document_type = Column(String(64), default="unknown", index=True)
    
    # Status: uploaded, processing, classified, extracted, validated, approved, rejected, failed
    status = Column(String(32), default="uploaded", index=True)
    confidence_score = Column(Float, default=0.0)
    page_count = Column(Integer, default=1)
    
    # Raw OCR full text
    raw_ocr_text = Column(Text, nullable=True)
    
    uploaded_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("User", back_populates="documents")
    jobs = relationship("ProcessingJob", back_populates="document", cascade="all, delete-orphan")
    fields = relationship("ExtractedField", back_populates="document", cascade="all, delete-orphan")
    runs = relationship("ExtractionRun", back_populates="document", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="document", cascade="all, delete-orphan")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(64), ForeignKey("documents.id"), nullable=False, index=True)
    task_id = Column(String(128), nullable=True)
    
    # status: queued, running, completed, failed
    status = Column(String(32), default="queued", index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    document = relationship("Document", back_populates="jobs")


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(64), ForeignKey("documents.id"), nullable=False, index=True)
    field_name = Column(String(64), nullable=False, index=True)
    field_value = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)
    page_number = Column(Integer, default=1)
    
    # Bounding box coordinates: {"x0": 0.1, "y0": 0.2, "x1": 0.4, "y1": 0.25} (normalized 0-1 or pixel)
    bounding_box = Column(JSON, nullable=True)
    
    is_verified = Column(Boolean, default=False)
    validation_status = Column(String(32), default="valid")  # valid, warning, error, unverified
    warning_message = Column(String(256), nullable=True)

    document = relationship("Document", back_populates="fields")


class ExtractionRun(Base):
    __tablename__ = "extraction_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(64), ForeignKey("documents.id"), nullable=False, index=True)
    model_name = Column(String(64), default="gemini-2.5-flash")
    model_version = Column(String(32), default="v1.0")
    raw_result = Column(JSON, nullable=True)
    validated_result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    document = relationship("Document", back_populates="runs")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(64), ForeignKey("documents.id"), nullable=False, index=True)
    field_id = Column(String(36), nullable=True)
    field_name = Column(String(64), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    modified_by = Column(String(64), default="human_operator")
    modified_at = Column(DateTime, default=utc_now)
    modified_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="audit_logs")
