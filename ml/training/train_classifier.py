"""
DocuMind AI - ML Document Classifier Training
Trains TF-IDF + Logistic Regression on labeled document corpus.
Outputs:
- ml/models/document_classifier.pkl (Complete Pipeline: Vectorizer + Classifier)
- ml/models/classes.json (Target class mappings)
- Evaluation metrics summary
"""

import os
import sys
import json
import joblib
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.datasets.sample_data import DOCUMENT_SAMPLES

def train_document_classifier():
    print("=" * 60)
    print("DocuMind AI: Training ML Document Classifier (TF-IDF + Logistic Regression)")
    print("=" * 60)

    texts = [s["text"] for s in DOCUMENT_SAMPLES]
    labels = [s["label"] for s in DOCUMENT_SAMPLES]

    print(f"Loaded {len(texts)} training samples across categories:")
    for label in sorted(list(set(labels))):
        count = labels.count(label)
        print(f"  - {label.upper()}: {count} samples")

    # Build Pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            strip_accents='unicode',
            lowercase=True,
            max_features=2500
        )),
        ('clf', LogisticRegression(
            C=5.0,
            max_iter=500,
            random_state=42,
            solver='lbfgs'
        ))
    ])

    pipeline.fit(texts, labels)

    # In-sample evaluation & validation
    preds = pipeline.predict(texts)
    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')

    print("\n--- Training Evaluation Metrics ---")
    print(f"Accuracy:        {acc * 100:.2f}%")
    print(f"Weighted F1:     {f1:.4f}")
    print(f"Weighted Prec:   {precision:.4f}")
    print(f"Weighted Recall: {recall:.4f}")
    print("\nClassification Report:\n", classification_report(labels, preds))

    # Save artifacts
    models_dir = PROJECT_ROOT / "ml" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    model_path = models_dir / "document_classifier.pkl"
    joblib.dump(pipeline, model_path)
    print(f"[OK] Saved model pipeline to: {model_path}")

    classes = sorted(list(set(labels)))
    classes_path = models_dir / "classes.json"
    with open(classes_path, "w") as f:
        json.dump({
            "classes": classes,
            "metrics": {
                "accuracy": acc,
                "f1_weighted": f1,
                "precision": precision,
                "recall": recall
            }
        }, f, indent=2)
    print(f"[OK] Saved classes metadata to: {classes_path}")

    # Verify predictions on test cases
    test_cases = [
        ("INVOICE #9081 Vendor: Oracle Corp Total: $14,000 Tax: $1,200", "invoice"),
        ("CAFE NERO Date: 09/11/2026 Latte $4.50 Total: $4.50 Paid with Debit", "receipt"),
        ("Jane Smith Senior ML Engineer Education: Stanford B.S. Skills: PyTorch, Python", "resume"),
        ("TENANT APPLICATION FORM Full Name: David Miller SSN: 000-11-2222 Address: 123 Main St", "application_form")
    ]

    print("\n--- Out-of-sample Verification Tests ---")
    for sample_text, expected in test_cases:
        pred_label = pipeline.predict([sample_text])[0]
        probs = pipeline.predict_proba([sample_text])[0]
        max_prob = max(probs)
        status = "[PASS]" if pred_label == expected else "[FAIL]"
        print(f"{status} Expected: {expected:<16} | Predicted: {pred_label:<16} | Confidence: {max_prob*100:.1f}%")

    print("\n[COMPLETE] Model training & verification completed successfully.")
    return pipeline

if __name__ == "__main__":
    train_document_classifier()
