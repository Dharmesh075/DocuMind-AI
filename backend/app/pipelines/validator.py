"""
DocuMind AI - Module 6: Data Validation Engine
Performs:
- Format validation (emails, dates, phone numbers, numeric values)
- Business logic validation (e.g., Invoice: Subtotal + Tax == Total)
- Required fields verification
- Flags warnings and errors on individual fields and the overall document
"""

import re
from typing import Any

def validate_extracted_fields(document_type: str, fields: list[dict], structured_data: dict[str, Any]) -> tuple[list[dict], list[str]]:
    """
    Validates field integrity and executes business rules.
    Returns:
    - updated fields with validation_status ('valid', 'warning', 'error') and warning_message
    - list of document-level validation alerts
    """
    doc_alerts = []
    field_map = {f["field_name"]: f for f in fields}

    # 1. Format validations
    for f in fields:
        name = f["field_name"]
        val = f.get("field_value")

        if val is None or val == "":
            f["validation_status"] = "warning"
            f["warning_message"] = "Field could not be extracted from document"
            continue

        # A field that passed extraction starts as valid; specific rules below
        # downgrade it to warning/error when needed.
        f["validation_status"] = "valid"
        f["warning_message"] = None

        # Email validation
        if "email" in name:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", str(val)):
                f["validation_status"] = "error"
                f["warning_message"] = "Invalid email format"
                doc_alerts.append(f"Invalid email: {val}")

        # Date validation
        if "date" in name:
            if not re.search(r"\d{1,4}[/\-\.]\d{1,2}[/\-\.]\d{2,4}", str(val)) and not re.search(r"[A-Za-z]{3,9}\s+\d{1,2}", str(val)):
                f["validation_status"] = "warning"
                f["warning_message"] = "Unusual date format"

        # Numeric validations
        if name in ["total", "subtotal", "tax", "total_amount"]:
            try:
                num = float(str(val).replace(",", ""))
                if num < 0:
                    f["validation_status"] = "error"
                    f["warning_message"] = "Amount cannot be negative"
            except ValueError:
                f["validation_status"] = "error"
                f["warning_message"] = "Invalid numerical amount"

    # 2. Business Logic Validation for Invoices
    if document_type.lower() == "invoice":
        subtotal_f = field_map.get("subtotal")
        tax_f = field_map.get("tax")
        total_f = field_map.get("total")

        subtotal = float(subtotal_f["field_value"].replace(",", "")) if subtotal_f and subtotal_f.get("field_value") else None
        tax = float(tax_f["field_value"].replace(",", "")) if tax_f and tax_f.get("field_value") else 0.0
        total = float(total_f["field_value"].replace(",", "")) if total_f and total_f.get("field_value") else None

        if subtotal is not None and total is not None:
            expected_total = subtotal + tax
            diff = abs(expected_total - total)
            tolerance = 0.50  # 50 cents tolerance for rounding discrepancies

            if diff > tolerance:
                msg = f"Arithmetic Mismatch: Subtotal ({subtotal:.2f}) + Tax ({tax:.2f}) = {expected_total:.2f}, but Total is {total:.2f} (diff: {diff:.2f})"
                if total_f:
                    total_f["validation_status"] = "error"
                    total_f["warning_message"] = msg
                doc_alerts.append(msg)
            elif total < subtotal:
                msg = f"Logical Anomaly: Total ({total:.2f}) is less than Subtotal ({subtotal:.2f})"
                if total_f:
                    total_f["validation_status"] = "error"
                    total_f["warning_message"] = msg
                doc_alerts.append(msg)
            else:
                if total_f and total_f.get("validation_status") == "valid":
                    total_f["warning_message"] = "Verified: Subtotal + Tax == Total"

    # 3. Required Fields Verification
    required_fields = {
        "invoice": ["invoice_number", "total"],
        "receipt": ["total_amount"],
        "resume": ["full_name", "email"],
        "application_form": ["applicant_name"]
    }.get(document_type.lower(), [])

    for req in required_fields:
        f = field_map.get(req)
        if not f or not f.get("field_value"):
            doc_alerts.append(f"Missing mandatory field: '{req}'")

    return fields, doc_alerts
