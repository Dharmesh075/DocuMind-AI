"""
DocuMind AI - Module 4: ML Document Classification
Predicts document type using TF-IDF + Logistic Regression model.
Categories: invoice, receipt, resume, application_form, unknown.
"""

import os
import joblib
from pathlib import Path
from app.core.config import settings

_MODEL_CACHE = None

def get_classifier():
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    model_path = settings.ML_MODELS_DIR / "document_classifier.pkl"
    if model_path.exists():
        try:
            _MODEL_CACHE = joblib.load(model_path)
            return _MODEL_CACHE
        except Exception as e:
            print(f"[Classifier] Failed to load trained model: {e}")
    return None

def heuristic_classification(text: str) -> tuple[str, float]:
    """Fallback classifier using domain keyword frequency."""
    text_lower = text.lower()

    scores = {
        "invoice": 0,
        "receipt": 0,
        "resume": 0,
        "application_form": 0
    }

    # Invoice signals
    if "invoice" in text_lower: scores["invoice"] += 4
    if "bill to" in text_lower or "billed to" in text_lower: scores["invoice"] += 3
    if "subtotal" in text_lower: scores["invoice"] += 2
    if "due date" in text_lower: scores["invoice"] += 2
    if "gstin" in text_lower or "vat" in text_lower: scores["invoice"] += 2

    # Receipt signals
    if "receipt" in text_lower: scores["receipt"] += 4
    if "cashier" in text_lower: scores["receipt"] += 3
    if "change due" in text_lower or "cash tendered" in text_lower: scores["receipt"] += 3
    if "visa" in text_lower or "mastercard" in text_lower or "amex" in text_lower: scores["receipt"] += 2

    # Resume signals
    if "resume" in text_lower or "curriculum vitae" in text_lower or "cv" in text_lower: scores["resume"] += 4
    if "education" in text_lower and "experience" in text_lower: scores["resume"] += 4
    if "skills" in text_lower: scores["resume"] += 2
    if "b.s." in text_lower or "bachelor" in text_lower or "m.s." in text_lower: scores["resume"] += 2

    # Application form signals
    if "application" in text_lower: scores["application_form"] += 4
    if "applicant" in text_lower: scores["application_form"] += 3
    if "date of birth" in text_lower or "dob" in text_lower: scores["application_form"] += 3
    if "signature" in text_lower: scores["application_form"] += 2

    best_type = max(scores, key=scores.get)
    max_score = scores[best_type]

    if max_score >= 3:
        conf = min(0.95, 0.50 + (max_score * 0.08))
        return best_type, round(conf, 3)
    return "unknown", 0.35

def classify_document(ocr_text: str) -> dict:
    if not ocr_text or len(ocr_text.strip()) < 10:
        return {
            "document_type": "unknown",
            "confidence": 0.0,
            "probabilities": {},
            "status": "unclassified"
        }

    clf = get_classifier()
    if clf is not None:
        try:
            raw_preds = clf.predict([ocr_text])[0]
            probs = clf.predict_proba([ocr_text])[0]
            pred_str = str(raw_preds)
            classes = [str(c) for c in clf.classes_]
            prob_dict = {str(cls): round(float(p), 4) for cls, p in zip(classes, probs)}
            max_prob = float(max(probs))

            # Unknown threshold
            if max_prob < 0.35:
                return {
                    "document_type": "unknown",
                    "confidence": round(max_prob, 3),
                    "probabilities": prob_dict,
                    "status": "classified"
                }

            return {
                "document_type": pred_str,
                "confidence": round(max_prob, 3),
                "probabilities": prob_dict,
                "status": "classified"
            }
        except Exception as e:
            print(f"[Classifier] Error predicting with model: {e}")

    # Fallback heuristic
    doc_type, conf = heuristic_classification(ocr_text)
    return {
        "document_type": doc_type,
        "confidence": conf,
        "probabilities": {doc_type: conf},
        "status": "classified"
    }
