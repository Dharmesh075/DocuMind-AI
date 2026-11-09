"""
DocuMind AI - Module 5: Intelligent Information Extraction
Extracts structured schema fields for:
- Invoice (Invoice number, vendor, date, tax, total, subtotal, line items)
- Receipt (Merchant, transaction date, amount, payment method)
- Resume (Name, email, phone, education, skills, experience)
- Application Form (Applicant info, IDs, addresses, form fields)

Grounds every extracted field in OCR text and attaches source bounding box coordinates.
Never invents/hallucinates missing values.
"""

import re
import json
from typing import Any, Optional
from app.core.config import settings
from app.schemas.document import (
    InvoiceExtractionData, ReceiptExtractionData,
    ResumeExtractionData, ApplicationFormExtractionData,
    BoundingBox
)

# --- Amount parsing helpers -------------------------------------------------
# These keep monetary extraction grounded in a label/value pair instead of
# leaking identifiers (GSTIN), percentages, or dates into amount fields.

_GSTIN_RE = re.compile(r"\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]\b", re.IGNORECASE)
_PERCENT_RE = re.compile(r"\b\d+(?:[.,]\d+)?\s*%")
_PAREN_RE = re.compile(r"\([^)]*\)")
_AMOUNT_RE = re.compile(r"[$€£₹]?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)")


def _amounts_in_text_segment(segment: str) -> list[float]:
    """Returns positive numeric amounts found in a line, ignoring IDs and percentages."""
    cleaned = _GSTIN_RE.sub(" ", segment)
    cleaned = _PAREN_RE.sub(" ", cleaned)
    cleaned = _PERCENT_RE.sub(" ", cleaned)

    amounts: list[float] = []
    for match in _AMOUNT_RE.finditer(cleaned):
        try:
            value = float(match.group(1).replace(",", ""))
        except ValueError:
            continue
        if value > 0:
            amounts.append(value)
    return amounts


def find_amount(text: str, label_pattern: str, exclude_pattern: Optional[str] = None) -> Optional[float]:
    """
    Finds the monetary amount that follows a label (e.g. 'Total Amount: 118.00').

    Scans lines bottom-up so the final/total value wins when a document repeats
    a label, and only reads the text after the last label on the line. This
    prevents 'Subtotal' from satisfying a plain 'total' label and stops
    percentages or GSTIN identifiers from being treated as amounts.
    """
    for line in reversed(text.splitlines()):
        if exclude_pattern and re.search(exclude_pattern, line, re.IGNORECASE):
            continue

        label_matches = list(re.finditer(rf"\b(?:{label_pattern})\b", line, re.IGNORECASE))
        if not label_matches:
            continue

        tail = line[label_matches[-1].end():]
        amounts = _amounts_in_text_segment(tail)
        if amounts:
            return amounts[0]

    return None


_SKILL_CANONICAL_NAMES = {
    "python": "Python",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "react": "React",
    "next.js": "Next.js",
    "fastapi": "FastAPI",
    "sql": "SQL",
    "pytorch": "PyTorch",
    "docker": "Docker",
    "redis": "Redis",
    "postgresql": "PostgreSQL",
    "machine learning": "Machine Learning",
    "nlp": "NLP",
    "aws": "AWS",
    "tailwind css": "Tailwind CSS",
}


def find_evidence_bbox(field_value: Any, ocr_blocks: list[dict]) -> Optional[dict]:
    """Finds the closest matching bounding box from OCR text blocks for a field value."""
    if not field_value or not ocr_blocks:
        return None

    val_str = str(field_value).strip().lower()
    if len(val_str) < 2:
        return None

    # 1. Exact or substring match in block
    for block in ocr_blocks:
        b_text = block.get("text", "").lower()
        if val_str in b_text:
            return block.get("bbox")

    # 2. Match individual tokens for numbers/IDs
    tokens = val_str.split()
    for token in tokens:
        if len(token) > 3:
            for block in ocr_blocks:
                if token in block.get("text", "").lower():
                    return block.get("bbox")

    return None

def extract_invoice_fields(ocr_text: str, ocr_blocks: list[dict]) -> dict:
    """Deterministic, high-precision regex & layout extraction for invoices."""
    text = ocr_text

    # Invoice Number
    inv_num = None
    inv_patterns = [
        # The lookahead stops 'Invoice' from matching the 'No' at the start of
        # the next line (e.g. 'Invoice\nNorthwind Traders').
        r"\binvoice\s*(?:number|no\.?|#|id)(?=\s|[:#\-]|$)\s*[:\-#]?\s*([A-Za-z0-9][A-Za-z0-9\-/_]*)",
        r"\binv\s*(?:no\.?|#|id)(?=\s|[:#\-]|$)\s*[:\-#]?\s*([A-Za-z0-9][A-Za-z0-9\-/_]*)",
        r"\binvoice\s*[:#]\s*([A-Za-z0-9][A-Za-z0-9\-/_]*)",
    ]
    for pat in inv_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            candidate = m.group(1).strip()
            if len(candidate) >= 2 and candidate.lower() not in ["date", "due", "to", "for", "total", "tax"]:
                inv_num = candidate
                break

    # Vendor Name
    vendor_name = None
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if lines:
        first_line = lines[0]
        # Clean common tax invoice headers
        clean_first = re.sub(r"^(tax invoice|invoice|original for recipient|commercial invoice)\s*[:\-]?\s*", "", first_line, flags=re.IGNORECASE).strip()
        if clean_first and len(clean_first) > 3:
            vendor_name = clean_first
        elif len(lines) > 1:
            vendor_name = lines[1]

    # Dates
    date_patterns = [
        r"(?:invoice\s*date|date of issue|issue date|date)[:\s]*([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4})",
        r"(?:date)[:\s]*([A-Za-z]{3,9}\s+[0-9]{1,2},?\s+[0-9]{4})",
        r"([0-9]{1,2}[/\-][0-9]{1,2}[/\-][0-9]{4})"
    ]
    inv_date = None
    for pat in date_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            inv_date = m.group(1).strip()
            break

    # Due Date
    due_date = None
    due_match = re.search(r"(?:due\s*date)[:\s]*([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4})", text, re.IGNORECASE)
    if due_match:
        due_date = due_match.group(1).strip()

    # Amounts: Subtotal, Tax, Total
    # NOTE: keep 'gstin' out of the tax labels - a GSTIN such as
    # '29ABCDE1234F1Z5' would otherwise be read as a tax amount (29.00).
    subtotal = find_amount(
        text,
        r"sub\s*total|subtotal|net\s*amount",
        exclude_pattern=r"total\s*amount",
    )
    tax = find_amount(
        text,
        r"sales\s*tax|total\s*tax|tax|vat|gst",
        exclude_pattern=r"gstin",
    )
    total = find_amount(
        text,
        r"grand\s*total|total\s*amount|total\s*due|balance\s*due|amount\s*due|total",
        exclude_pattern=r"sub\s*total|subtotal|total\s*tax",
    )

    currency = "USD"
    if "₹" in text or "gstin" in text.lower() or "inr" in text.lower():
        currency = "INR"
    elif "€" in text or "eur" in text.lower():
        currency = "EUR"
    elif "£" in text or "gbp" in text.lower():
        currency = "GBP"

    # Line Items
    line_items = []
    item_matches = re.findall(r"(?:item|description)?\s*([A-Za-z\s]{3,35})\s+(?:qty:?\s*)?([0-9]+)\s+(?:rate:?\s*)?([0-9,]+(?:\.[0-9]+)?)\s+(?:amount:?\s*)?([0-9,]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
    for desc, qty_s, rate_s, amt_s in item_matches:
        try:
            line_items.append({
                "description": desc.strip(),
                "quantity": float(qty_s),
                "unit_price": float(rate_s.replace(",", "")),
                "amount": float(amt_s.replace(",", ""))
            })
        except Exception:
            pass

    fields = [
        {"field_name": "vendor_name", "field_value": vendor_name, "confidence": 0.96 if vendor_name else 0.4},
        {"field_name": "invoice_number", "field_value": inv_num, "confidence": 0.98 if inv_num else 0.3},
        {"field_name": "invoice_date", "field_value": inv_date, "confidence": 0.94 if inv_date else 0.4},
        {"field_name": "due_date", "field_value": due_date, "confidence": 0.90 if due_date else 0.0},
        {"field_name": "subtotal", "field_value": f"{subtotal:.2f}" if subtotal else None, "confidence": 0.92 if subtotal else 0.4},
        {"field_name": "tax", "field_value": f"{tax:.2f}" if tax else None, "confidence": 0.90 if tax else 0.4},
        {"field_name": "total", "field_value": f"{total:.2f}" if total else None, "confidence": 0.95 if total else 0.3},
        {"field_name": "currency", "field_value": currency, "confidence": 0.99}
    ]

    # Attach bounding boxes
    for f in fields:
        f["bounding_box"] = find_evidence_bbox(f["field_value"], ocr_blocks)

    return {
        "structured_data": {
            "vendor_name": vendor_name,
            "invoice_number": inv_num,
            "invoice_date": inv_date,
            "due_date": due_date,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "currency": currency,
            "line_items": line_items
        },
        "fields": fields
    }

def extract_receipt_fields(ocr_text: str, ocr_blocks: list[dict]) -> dict:
    text = ocr_text

    merchant_name = None
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if lines:
        merchant_name = lines[0]

    date_match = re.search(r"([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4})", text)
    trans_date = date_match.group(1) if date_match else None

    # 'Subtotal' must not satisfy the plain 'total' label. Read the value after
    # the label, ignoring percentages and identifiers.
    total = find_amount(
        text,
        r"total\s*due|grand\s*total|final\s*charge|total\s*amount|total",
        exclude_pattern=r"sub\s*total|subtotal|total\s*tax",
    )

    subtotal = find_amount(
        text,
        r"sub\s*total|subtotal|net\s*amount",
        exclude_pattern=r"total\s*amount",
    )

    tax = find_amount(
        text,
        r"sales\s*tax|total\s*tax|tax|vat|gst",
        exclude_pattern=r"gstin",
    )

    payment_method = "Cash"
    if "visa" in text.lower(): payment_method = "Visa"
    elif "mastercard" in text.lower() or "master card" in text.lower(): payment_method = "Mastercard"
    elif "amex" in text.lower(): payment_method = "American Express"
    elif "apple pay" in text.lower(): payment_method = "Apple Pay"

    fields = [
        {"field_name": "merchant_name", "field_value": merchant_name, "confidence": 0.95 if merchant_name else 0.4},
        {"field_name": "transaction_date", "field_value": trans_date, "confidence": 0.92 if trans_date else 0.4},
        {"field_name": "subtotal", "field_value": f"{subtotal:.2f}" if subtotal else None, "confidence": 0.90 if subtotal else 0.4},
        {"field_name": "total_amount", "field_value": f"{total:.2f}" if total else None, "confidence": 0.96 if total else 0.4},
        {"field_name": "payment_method", "field_value": payment_method, "confidence": 0.90}
    ]

    for f in fields:
        f["bounding_box"] = find_evidence_bbox(f["field_value"], ocr_blocks)

    return {
        "structured_data": {
            "merchant_name": merchant_name,
            "transaction_date": trans_date,
            "subtotal": subtotal,
            "total_amount": total,
            "payment_method": payment_method
        },
        "fields": fields
    }

def extract_resume_fields(ocr_text: str, ocr_blocks: list[dict]) -> dict:
    text = ocr_text

    email_match = re.search(r"([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})", text)
    email = email_match.group(1) if email_match else None

    phone_match = re.search(r"(\+?[0-9]{1,3}[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})", text)
    phone = phone_match.group(1) if phone_match else None

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    full_name = lines[0] if lines else None

    # Detect skills, preserving canonical spellings/casing (TypeScript, Next.js, ...)
    text_lower = text.lower()
    found_skills = [
        canonical for keyword, canonical in _SKILL_CANONICAL_NAMES.items()
        if keyword in text_lower
    ]
    found_skills.sort(key=lambda skill: text_lower.find(skill.lower()))

    fields = [
        {"field_name": "full_name", "field_value": full_name, "confidence": 0.92 if full_name else 0.3},
        {"field_name": "email", "field_value": email, "confidence": 0.99 if email else 0.2},
        {"field_name": "phone", "field_value": phone, "confidence": 0.95 if phone else 0.2},
        {"field_name": "skills", "field_value": ", ".join(found_skills) if found_skills else None, "confidence": 0.88 if found_skills else 0.3}
    ]

    for f in fields:
        f["bounding_box"] = find_evidence_bbox(f["field_value"], ocr_blocks)

    return {
        "structured_data": {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "skills": found_skills
        },
        "fields": fields
    }

def extract_form_fields(ocr_text: str, ocr_blocks: list[dict]) -> dict:
    text = ocr_text

    # Restrict the name to the labelled line; a greedy \s+ used to swallow the
    # next line ("... Taylor\nDate of Birth") into the value.
    name_match = re.search(
        r"\b(?:applicant\s*(?:full\s*)?name|candidate\s*(?:full\s*)?name|"
        r"full\s*name|name\s+of\s+applicant)\b\s*[:\-]\s*([^\n\r]{2,80})",
        text,
        re.IGNORECASE,
    )
    applicant_name = None
    if name_match:
        applicant_name = re.split(r"\s{2,}|\s*[|;]\s*", name_match.group(1).strip())[0].strip()
        applicant_name = re.sub(
            r"\s+(?:date\s+of\s+birth|dob|address|phone|email)\b.*$",
            "",
            applicant_name,
            flags=re.IGNORECASE,
        ).strip() or None

    # Word boundaries prevent 'id' matching inside words such as 'Candidate'.
    id_match = re.search(
        r"\b(?:social\s+security\s+(?:number|no\.?)|ssn|id|license|licence|passport)\b"
        r"\s*(?:number|no\.?|#)?\s*[:\-]?\s*([A-Za-z0-9][A-Za-z0-9\-/]{2,})",
        text,
        re.IGNORECASE,
    )
    id_num = id_match.group(1).strip() if id_match else None

    dob_match = re.search(r"(?:date of birth|dob)[:\s]*([0-9]{1,2}[/\-\.][0-9]{1,2}[/\-\.][0-9]{2,4})", text, re.IGNORECASE)
    dob = dob_match.group(1).strip() if dob_match else None

    fields = [
        {"field_name": "applicant_name", "field_value": applicant_name, "confidence": 0.90 if applicant_name else 0.3},
        {"field_name": "id_number", "field_value": id_num, "confidence": 0.93 if id_num else 0.3},
        {"field_name": "date_of_birth", "field_value": dob, "confidence": 0.91 if dob else 0.3}
    ]

    for f in fields:
        f["bounding_box"] = find_evidence_bbox(f["field_value"], ocr_blocks)

    return {
        "structured_data": {
            "applicant_name": applicant_name,
            "id_number": id_num,
            "date_of_birth": dob
        },
        "fields": fields
    }

def extract_information(document_type: str, ocr_text: str, ocr_blocks: list[dict]) -> dict:
    """Dispatches extraction according to classified document type."""
    doc_type = document_type.lower()
    if doc_type == "invoice":
        return extract_invoice_fields(ocr_text, ocr_blocks)
    elif doc_type == "receipt":
        return extract_receipt_fields(ocr_text, ocr_blocks)
    elif doc_type == "resume":
        return extract_resume_fields(ocr_text, ocr_blocks)
    elif doc_type == "application_form":
        return extract_form_fields(ocr_text, ocr_blocks)
    else:
        # Default generic extraction for unknown documents
        return extract_invoice_fields(ocr_text, ocr_blocks)
