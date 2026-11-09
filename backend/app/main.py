"""
DocuMind AI - FastAPI Application Entrypoint
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.database.session import init_db, SessionLocal
from app.models.document import Document
from app.api.routes import documents, analytics, jobs
from app.services.document_service import process_document_pipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables on startup
    init_db()

    # Seed sample documents if database is empty
    db = SessionLocal()
    try:
        count = db.query(Document).count()
        if count == 0:
            print("[DocuMind Startup] Seeding initial test documents for dashboard & review...")
            # We will generate a sample invoice, receipt, and resume
            from app.api.routes.documents import create_sample_document
            create_sample_document("invoice", db)
            create_sample_document("receipt", db)
            create_sample_document("resume", db)
            print("[DocuMind Startup] Seeded 3 sample documents successfully.")
    except Exception as e:
        print(f"[DocuMind Startup] Seeding notice: {e}")
    finally:
        db.close()

    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Intelligent Document Processing system with Apple-inspired Liquid Glass interface.",
    lifespan=lifespan
)

# Enable CORS for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(jobs.router, prefix=settings.API_V1_PREFIX)

# Mount Static Storage for Document Previews
app.mount("/storage/documents", StaticFiles(directory=str(settings.STORAGE_DIR)), name="storage")

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "tagline": "Transforming unstructured documents into intelligent data.",
        "version": settings.APP_VERSION,
        "status": "online",
        "docs_url": "/docs"
    }

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "storage_backend": settings.STORAGE_BACKEND,
        "ocr_engine": "paddleocr/pymupdf/opencv",
        "ml_classifier": "scikit-learn tfidf-logistic-regression"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
