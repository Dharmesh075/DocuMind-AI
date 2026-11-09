"""
DocuMind AI - Backend & Pipeline Tests
"""

import sys
from pathlib import Path

# Add backend directory to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.pipelines.classifier import classify_document
from app.pipelines.validator import validate_extracted_fields
from app.pipelines.extractor import (
    extract_invoice_fields,
    extract_receipt_fields,
    extract_form_fields,
    extract_resume_fields,
)
from app.pipelines.confidence import compute_field_confidence, compute_document_confidence
from app.database.session import init_db, SessionLocal
from app.models.document import Document
from app.api.routes.documents import create_sample_document

def test_classifier_predictions():
    inv_text = "INVOICE Number: INV-9901 Date: 09/11/2026 Vendor: Apex Technologies Subtotal: 1000 Total: 1180"
    res = classify_document(inv_text)
    assert res["document_type"] == "invoice"
    assert res["confidence"] > 0.40

    resume_text = "Alexander Chen Senior Machine Learning Engineer Education: UC Berkeley Skills: Python, PyTorch, React"
    res_resume = classify_document(resume_text)
    assert res_resume["document_type"] == "resume"
    assert res_resume["confidence"] > 0.35

def test_extraction_pipeline():
    sample_ocr = "TAX INVOICE ABC Technologies Pvt Ltd\nInvoice Number: INV-1024 Date: 09/11/2026\nSubtotal: 10000.00\nTax: 1800.00\nTotal Amount: 11800.00"
    blocks = [
        {"text": "Invoice Number: INV-1024", "bbox": {"x0": 0.1, "y0": 0.1, "x1": 0.4, "y1": 0.14}},
        {"text": "Subtotal: 10000.00", "bbox": {"x0": 0.1, "y0": 0.5, "x1": 0.4, "y1": 0.54}},
        {"text": "Total Amount: 11800.00", "bbox": {"x0": 0.1, "y0": 0.6, "x1": 0.4, "y1": 0.64}}
    ]
    res = extract_invoice_fields(sample_ocr, blocks)
    fields = {f["field_name"]: f for f in res["fields"]}

    assert fields["invoice_number"]["field_value"] == "INV-1024"
    assert fields["total"]["field_value"] == "11800.00"
    assert fields["invoice_number"]["bounding_box"] is not None

def test_invoice_tax_is_not_taken_from_gstin():
    """A GSTIN like 29ABCDE1234F1Z5 must not be parsed as a tax amount."""
    sample_ocr = (
        "TAX INVOICE ABC Technologies Pvt Ltd\n"
        "Northwind Traders Ltd\n"
        "Invoice Number: INV-1024 Date: 09/11/2026\n"
        "Bill To: Acme Corp GSTIN: 29ABCDE1234F1Z5\n"
        "Item Description: Cloud Architecture Consulting Qty: 40 Rate: 250 Amount: 10000\n"
        "Subtotal: 10000.00\n"
        "Tax (SGST+CGST 18%): 1800.00\n"
        "Total Amount: 11800.00"
    )
    res = extract_invoice_fields(sample_ocr, [])
    fields = {f["field_name"]: f for f in res["fields"]}

    assert fields["subtotal"]["field_value"] == "10000.00"
    assert fields["tax"]["field_value"] == "1800.00"
    assert fields["total"]["field_value"] == "11800.00"

    validated, alerts = validate_extracted_fields("invoice", res["fields"], res["structured_data"])
    total_field = next(f for f in validated if f["field_name"] == "total")
    assert total_field["validation_status"] == "valid"
    assert alerts == []


def test_receipt_total_is_not_the_subtotal():
    """'Subtotal' contains the word 'total' but must not satisfy the total label."""
    sample_ocr = (
        "STARBUCKS COFFEE STORE #14092\n"
        "DATE: 11/08/2026 08:42 AM\n"
        "Subtotal: $9.20\n"
        "Tax: $0.78\n"
        "TOTAL: $9.98\n"
        "PAYMENT METHOD: VISA CONTACTLESS"
    )
    res = extract_receipt_fields(sample_ocr, [])
    fields = {f["field_name"]: f for f in res["fields"]}

    assert fields["subtotal"]["field_value"] == "9.20"
    assert fields["total_amount"]["field_value"] == "9.98"


def test_application_form_fields_stay_on_their_lines():
    sample_ocr = (
        "APPLICATION FOR EMPLOYMENT\n"
        "Candidate Application Form\n"
        "Applicant Full Name: Robert Michael Taylor\n"
        "Date of Birth: 14/05/1992\n"
        "Social Security Number / ID: XXX-XX-4819"
    )
    res = extract_form_fields(sample_ocr, [])
    fields = {f["field_name"]: f for f in res["fields"]}

    assert fields["applicant_name"]["field_value"] == "Robert Michael Taylor"
    assert fields["id_number"]["field_value"] == "XXX-XX-4819"
    assert fields["date_of_birth"]["field_value"] == "14/05/1992"


def test_resume_skills_keep_canonical_casing():
    sample_ocr = (
        "ALEXANDER CHEN\n"
        "Email: alex.chen@example.com | Phone: +1-555-019-2834\n"
        "SKILLS: Python, TypeScript, Next.js, React, FastAPI, PostgreSQL"
    )
    res = extract_resume_fields(sample_ocr, [])
    fields = {f["field_name"]: f for f in res["fields"]}

    skills = [s.strip() for s in fields["skills"]["field_value"].split(",")]
    assert "TypeScript" in skills
    assert "Next.js" in skills
    assert "FastAPI" in skills
    assert "PostgreSQL" in skills


def test_validation_arithmetic():
    # Valid arithmetic
    clean_fields = [
        {"field_name": "invoice_number", "field_value": "INV-1024", "confidence": 0.98},
        {"field_name": "subtotal", "field_value": "100.00", "confidence": 0.95},
        {"field_name": "tax", "field_value": "18.00", "confidence": 0.95},
        {"field_name": "total", "field_value": "118.00", "confidence": 0.95}
    ]
    validated, clean_alerts = validate_extracted_fields("invoice", clean_fields, {})
    assert len(clean_alerts) == 0

    # Inconsistent arithmetic (subtotal 100 + tax 18 != total 150)
    dirty_fields = [
        {"field_name": "invoice_number", "field_value": "INV-1024", "confidence": 0.98},
        {"field_name": "subtotal", "field_value": "100.00", "confidence": 0.95},
        {"field_name": "tax", "field_value": "18.00", "confidence": 0.95},
        {"field_name": "total", "field_value": "150.00", "confidence": 0.95}
    ]
    validated, dirty_alerts = validate_extracted_fields("invoice", dirty_fields, {})
    assert len(dirty_alerts) > 0
    assert any("Arithmetic Mismatch" in a for a in dirty_alerts)

def test_database_and_sample_seeding():
    init_db()
    db = SessionLocal()
    try:
        res = create_sample_document("invoice", db)
        assert res["status"] == "created_and_processed"
        doc_id = res["document_id"]

        doc = db.query(Document).filter(Document.id == doc_id).first()
        assert doc is not None
        assert doc.document_type == "invoice"
        assert len(doc.fields) > 0
    finally:
        db.close()
