"""
DocuMind AI - Pydantic Schemas & DTOs
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    x0: float = Field(..., description="Left edge (0-1 normalized)")
    y0: float = Field(..., description="Top edge (0-1 normalized)")
    x1: float = Field(..., description="Right edge (0-1 normalized)")
    y1: float = Field(..., description="Bottom edge (0-1 normalized)")

class ExtractedFieldItem(BaseModel):
    id: str
    field_name: str
    field_value: Optional[str] = None
    confidence: float = 1.0
    page_number: int = 1
    bounding_box: Optional[BoundingBox] = None
    is_verified: bool = False
    validation_status: str = "valid"
    warning_message: Optional[str] = None

class ExtractedFieldUpdate(BaseModel):
    field_value: str
    modified_by: Optional[str] = "human_operator"

class AuditLogItem(BaseModel):
    id: str
    field_id: Optional[str] = None
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    modified_by: str
    modified_at: datetime

# --- Specific Extraction Schemas ---

class InvoiceLineItem(BaseModel):
    description: str
    quantity: Optional[float] = 1.0
    unit_price: Optional[float] = 0.0
    amount: float

class InvoiceExtractionData(BaseModel):
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    currency: str = "USD"
    line_items: list[InvoiceLineItem] = []
    payment_terms: Optional[str] = None

class ReceiptExtractionData(BaseModel):
    merchant_name: Optional[str] = None
    transaction_date: Optional[str] = None
    total_amount: Optional[float] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    payment_method: Optional[str] = None
    items: list[str] = []

class ResumeExtractionData(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    skills: list[str] = []
    education: list[str] = []
    experience: list[str] = []
    summary: Optional[str] = None

class ApplicationFormExtractionData(BaseModel):
    applicant_name: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    form_fields: dict[str, Any] = {}

# --- Document Summary & Detail ---

class DocumentSummary(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    document_type: str
    status: str
    confidence_score: float
    page_count: int
    uploaded_at: datetime
    updated_at: datetime

class DocumentDetail(DocumentSummary):
    raw_ocr_text: Optional[str] = None
    preview_url: Optional[str] = None
    fields: list[ExtractedFieldItem] = []
    audit_logs: list[AuditLogItem] = []
    structured_data: Optional[dict[str, Any]] = None

class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    is_duplicate: bool = False
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    document_id: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class AnalyticsResponse(BaseModel):
    total_documents: int
    successfully_processed: int
    processing: int
    needs_review: int
    document_type_distribution: dict[str, int]
    status_distribution: dict[str, int]
    avg_confidence_score: float
    avg_processing_time_sec: float
