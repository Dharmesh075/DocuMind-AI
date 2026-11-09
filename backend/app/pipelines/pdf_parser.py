"""
DocuMind AI - Module 3: PDF Parser & Text Extractor
Checks whether a PDF contains selectable text before falling back to OCR.
"""

import re
from pathlib import Path
from typing import Optional

def extract_text_from_pdf_stream(file_path: str) -> Optional[dict]:
    """
    Attempts direct text extraction from PDF using fitz (PyMuPDF)
    or native stream parsing for selectable digital PDFs.
    """
    # 1. Try PyMuPDF (package is imported as `pymupdf`; `fitz` is the legacy name)
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        doc = fitz.open(file_path)
        total_text = []
        blocks = []
        page_count = len(doc)

        for page_idx, page in enumerate(doc):
            w = page.rect.width
            h = page.rect.height
            page_blocks = page.get_text("blocks")
            for b in page_blocks:
                # b: (x0, y0, x1, y1, text, block_no, block_type)
                if len(b) >= 5 and b[4].strip():
                    text = b[4].strip()
                    total_text.append(text)
                    blocks.append({
                        "text": text,
                        "page": page_idx + 1,
                        "confidence": 0.99,
                        "bbox": {
                            "x0": round(b[0] / w, 4),
                            "y0": round(b[1] / h, 4),
                            "x1": round(b[2] / w, 4),
                            "y1": round(b[3] / h, 4),
                        }
                    })

        full_text = "\n".join(total_text)
        if len(full_text.strip()) > 30:
            return {
                "text": full_text,
                "page_count": page_count,
                "blocks": blocks,
                "method": "digital_pdf_selectable"
            }
    except Exception:
        pass

    # 2. Native PDF text stream parser fallback
    try:
        with open(file_path, "rb") as f:
            content = f.read()

        # Look for text streams inside BT (Begin Text) ... ET (End Text) blocks
        stream_matches = re.findall(rb"BT\s*(.*?)\s*ET", content, re.DOTALL)
        extracted_lines = []
        for sm in stream_matches:
            # Extract strings inside parentheses like (Invoice #1024)
            strings = re.findall(r"\((.*?)\)", sm.decode("latin1", errors="ignore"))
            if strings:
                line = " ".join(strings).strip()
                if line:
                    extracted_lines.append(line)

        if extracted_lines:
            combined = "\n".join(extracted_lines)
            if len(combined.strip()) > 20:
                blocks = []
                for idx, line in enumerate(extracted_lines):
                    blocks.append({
                        "text": line,
                        "page": 1,
                        "confidence": 0.95,
                        "bbox": {
                            "x0": 0.1,
                            "y0": round(0.1 + (idx * 0.03), 4),
                            "x1": 0.9,
                            "y1": round(0.12 + (idx * 0.03), 4),
                        }
                    })
                return {
                    "text": combined,
                    "page_count": 1,
                    "blocks": blocks,
                    "method": "pdf_stream_decompressed"
                }
    except Exception:
        pass

    return None
