# DocuMind AI

> **Transforming unstructured documents into intelligent data.**

DocuMind AI is an enterprise-grade **Intelligent Document Processing (IDP)** system built with an **Apple-inspired Liquid Glass** user interface, a **FastAPI** AI/ML backend, automated layout understanding, ML classification, grounded information extraction, arithmetic validation, and an interactive **Human-in-the-Loop (HITL)** review workspace.

---

## 🌟 Key Features

1. **Apple-Inspired Liquid Glass UI**:
   - Translucent frosted glass navigation, floating action bars, and subtle specular borders.
   - Dark-first midnight aesthetic (`#070A12`) with ambient radial mesh glow.
   - Built with Next.js 16 App Router, TypeScript, Tailwind CSS, and Lucide icons.

2. **Interactive Split-Screen Review Workspace**:
   - **Left Panel (Document Canvas)**: High-resolution document preview with interactive bounding box overlays and zoom controls.
   - **Right Panel (Grounded Field Inspector)**: Field-level confidence pills (Green >90%, Amber 70-89%, Red <70%), validation warning alerts, inline editing with one-click audit logging, document approval, and JSON/CSV export.
   - **Bi-directional Coordination**: Hovering or clicking any extracted field highlights its exact bounding box on the original document, and clicking any bounding box on the document focuses that field in the inspector.

3. **7-Stage AI/ML Processing Pipeline**:
   - **Module 1 (Ingestion)**: SHA-256 duplicate detection, MIME signature validation, file size limits.
   - **Module 2 (Preprocessing)**: Deskewing, contrast normalization, and preview rendering via OpenCV.
   - **Module 3 (OCR & Layout Analysis)**: Digital PDF selectable stream extraction + OCR fallback with bounding box coordinates and reading order.
   - **Module 4 (ML Classification)**: Scikit-learn TF-IDF + Logistic Regression baseline trained on representative corpus across 4 categories (Invoices, Receipts, Resumes, Application Forms).
   - **Module 5 (Intelligent Extraction)**: Grounded structured JSON extraction grounded in OCR tokens. Strict non-hallucination policy (unverified fields return `null` and flag review).
   - **Module 6 (Data Validation & Confidence Scoring)**: Rule-based regex validation, arithmetic verification for invoices (`subtotal + tax == total`), and composite multi-factor confidence scoring.
   - **Module 7 (Human-in-the-Loop)**: Field-level inline editing, instant recalculation, audit history tracking, and one-click approval.

---

## 🔭 Reference Architecture

The processing stages mirror the [AWS GenAI Intelligent Document Processing
accelerator](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws):
OCR → document classification → grounded extraction → rule validation →
confidence assessment → human review. This repository keeps that flow local
and self-hosted, using FastAPI, scikit-learn, PyMuPDF, and OpenCV instead of
managed AWS services such as Textract and Bedrock.

---

## 🏗️ System Architecture

```
                          ┌───────────────────────────┐
                          │    Next.js 16 Frontend    │
                          │   Apple Liquid Glass UI   │
                          └─────────────┬─────────────┘
                                        │ REST API
                                        ▼
                          ┌───────────────────────────┐
                          │      FastAPI Backend      │
                          │   Modular REST Services   │
                          └─────────────┬─────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│  File & Preview DB  │      │ Background Workers  │      │ SQLAlchemy / DB     │
│   storage/documents │      │   Celery / Redis    │      │ SQLite / PostgreSQL │
└─────────────────────┘      └──────────┬──────────┘      └─────────────────────┘
                                        │
                                        ▼
        ┌───────────────────────────────────────────────────────────────┐
        │                 7-Stage AI/ML Processing Pipeline             │
        │  1. Ingestion  -> 2. Preprocess -> 3. OCR & Layout            │
        │  4. ML Classifier (TF-IDF + LR) -> 5. Structured Extractor    │
        │  6. Business Validator          -> 7. Human Review Loop       │
        └───────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
DocuMind-AI/
├── frontend/                     # Next.js App Router Frontend
│   ├── app/
│   │   ├── page.tsx              # Operations Center Dashboard
│   │   ├── documents/            # Document Repository & Filters
│   │   ├── upload/               # Drag & Drop Liquid Glass Dropzone
│   │   ├── review/[id]/          # Split-Screen Review Workspace
│   │   ├── analytics/            # System Telemetry & ML Benchmarks
│   │   ├── settings/             # AI Pipeline & Threshold Settings
│   │   └── layout.tsx            # Global Liquid Glass Shell
│   ├── components/
│   │   ├── dashboard/            # Sidebar, TopNavbar, StatsCard
│   │   ├── documents/            # DocumentTable
│   │   └── review/               # DocumentViewer, ExtractionReviewPanel, AuditDrawer
│   ├── lib/                      # Typed API Service Client
│   └── styles/                   # globals.css (Liquid Glass variables & styles)
├── backend/                      # FastAPI Python Application
│   ├── app/
│   │   ├── api/routes/           # documents, analytics, jobs endpoints
│   │   ├── core/                 # Config & Pydantic settings
│   │   ├── database/             # SQLAlchemy engine & session
│   │   ├── models/               # Document, Job, ExtractedField, AuditLog models
│   │   ├── schemas/              # Pydantic schemas (Invoices, Receipts, Resumes, Forms)
│   │   ├── pipelines/            # Ingestion, Preprocessing, OCR, Classifier, Extractor, Validator
│   │   ├── services/             # Document pipeline orchestrator
│   │   └── workers/              # Celery background task worker
│   ├── storage/documents/        # File repository & rendered preview images
│   └── requirements.txt
├── ml/                           # Data Science & Machine Learning
│   ├── datasets/                 # Labeled corpus across 4 document types
│   ├── models/                   # Serialized document_classifier.pkl & classes.json
│   ├── training/                 # train_classifier.py
│   └── evaluation/               # evaluate_models.py (CER, WER, Exact-Match)
├── tests/
│   └── backend/                  # pytest suite (Classifier, Extraction, Validator, DB)
├── infrastructure/               # Docker configs & scripts
├── docker-compose.yml            # Multi-container production stack
├── start_platform.py             # Single-command launcher for local dev
├── start_platform.bat
└── README.md
```

---

## ⚡ Quickstart

### 1. Prerequisites
- **Python 3.10+** (FastAPI, scikit-learn, OpenCV, PyMuPDF)
- **Node.js 18+** (Next.js)

Install the Python dependencies once:

```bash
pip install -r backend/requirements.txt
```

> **OCR note:** digital PDFs are read directly through PyMuPDF. Scanned PDFs
> and images use PaddleOCR or Tesseract when those optional engines are
> installed. Without an OCR engine, raster documents are safely flagged for
> human review instead of producing garbage fields.

### 2. Launch Local Platform Concurrently

Run the included launcher to start both FastAPI (port 8000) and Next.js (port 3000):

```bash
python start_platform.py
```
*(Or double-click `start_platform.bat` on Windows)*

Then open:
- **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
- **Backend API & Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Testing & Evaluation

### Run Backend Pytest Suite
```bash
python -m pytest tests/backend/test_api.py -v
```
All 8 core unit tests verify:
- TF-IDF + Logistic Regression classification predictions.
- Structured invoice field extraction and bounding box alignment.
- Invoice tax extraction is not confused by GSTIN identifiers.
- Receipt totals are not confused with the subtotal line.
- Application-form fields stay on their labelled lines.
- Resume skills keep canonical casing (TypeScript, Next.js, FastAPI).
- Business rule arithmetic validation (`subtotal + tax == total`).
- Database schema persistence and automatic sample seeding.

### Run ML Evaluation Benchmark
```bash
python ml/evaluation/evaluate_models.py
```
Evaluates Character Error Rate (CER), Word Error Rate (WER), and field Exact-Match (EM) metrics.

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/documents/upload` | Ingests document via multipart, binary, or base64 JSON |
| `GET` | `/api/v1/documents` | Lists documents with status and category filtering |
| `GET` | `/api/v1/documents/{id}` | Retrieves document detail, fields, bounding boxes, and audit history |
| `GET` | `/api/v1/documents/{id}/preview` | Streams high-res rendered preview image for the canvas viewer |
| `POST` | `/api/v1/documents/{id}/process` | Triggers background processing pipeline |
| `GET` | `/api/v1/documents/{id}/results` | Returns pure structured JSON extraction payload |
| `PATCH` | `/api/v1/documents/{id}/fields/{field_id}` | Human-in-the-Loop inline field edit with audit log recording |
| `POST` | `/api/v1/documents/{id}/approve` | Marks document verified and approved by human operator |
| `POST` | `/api/v1/documents/{id}/reprocess` | Re-executes the extraction pipeline |
| `GET` | `/api/v1/documents/{id}/export` | Exports structured results as JSON or CSV |
| `GET` | `/api/v1/analytics` | Telemetry, confidence averages, and category distribution |
| `POST` | `/api/v1/documents/sample/{type}` | Generates and processes a demo Invoice, Receipt, Resume, or Form |

---

## 🐳 Docker Deployment

To launch the full production environment with PostgreSQL, Redis, Celery, MinIO, FastAPI, and Next.js:

```bash
docker-compose up --build
```
