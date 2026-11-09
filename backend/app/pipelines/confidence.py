"""
DocuMind AI - Module 6: Confidence Scoring
Computes composite multi-factor confidence scores for fields and the overall document.
Factors:
- OCR recognition confidence
- Evidence bounding box presence
- Validation status (clean vs warning vs error)
- Completeness of required fields
"""

def compute_field_confidence(field: dict) -> float:
    base_conf = float(field.get("confidence", 0.80))
    val_status = field.get("validation_status", "valid")
    has_bbox = field.get("bounding_box") is not None
    has_value = bool(field.get("field_value"))

    if not has_value:
        return 0.20

    score = base_conf

    # Bonus for evidence bounding box located in document
    if has_bbox:
        score = min(0.99, score + 0.05)

    # Penalties for validation issues
    if val_status == "warning":
        score = max(0.40, score - 0.15)
    elif val_status == "error":
        score = max(0.20, score - 0.40)

    return round(score, 3)

def compute_document_confidence(fields: list[dict], doc_alerts: list[str]) -> float:
    if not fields:
        return 0.0

    field_scores = [f.get("confidence", 0.5) for f in fields]
    avg_score = sum(field_scores) / len(field_scores)

    # Penalize for document-level validation alerts (e.g. arithmetic errors)
    penalty = min(0.30, len(doc_alerts) * 0.10)
    final_score = max(0.10, avg_score - penalty)

    return round(final_score, 3)
