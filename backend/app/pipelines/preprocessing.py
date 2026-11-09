"""
DocuMind AI - Module 2: Document Preprocessing
Handles image normalization, deskewing, and preview rendering for the frontend.
"""

import os
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from app.core.config import settings

def deskew_image(image_np: np.ndarray) -> np.ndarray:
    """Estimates skew angle using minAreaRect and rotates image to deskew."""
    try:
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY) if len(image_np.shape) == 3 else image_np
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 50:
            return image_np
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        if abs(angle) > 0.5 and abs(angle) < 45.0:
            (h, w) = image_np.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image_np, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated
    except Exception:
        pass
    return image_np

def generate_document_preview(file_path: str, doc_id: str) -> str:
    """
    Renders a standard preview image for the document.
    Outputs preview PNG path stored in storage.
    """
    ext = Path(file_path).suffix.lower()
    preview_filename = f"preview_{doc_id}.png"
    preview_path = settings.STORAGE_DIR / preview_filename

    if ext in [".png", ".jpg", ".jpeg"]:
        img = cv2.imread(file_path)
        if img is not None:
            # Apply deskew and resize if overly massive
            deskewed = deskew_image(img)
            h, w = deskewed.shape[:2]
            target_w = min(1200, w)
            target_h = int(h * (target_w / w))
            resized = cv2.resize(deskewed, (target_w, target_h), interpolation=cv2.INTER_AREA)
            cv2.imwrite(str(preview_path), resized)
            return str(preview_path)

    # For PDFs or fallback rendering
    # Try PyMuPDF if available
    try:
        try:
            import pymupdf as fitz
        except ImportError:
            import fitz
        doc = fitz.open(file_path)
        if len(doc) > 0:
            page = doc[0]
            pix = page.get_pixmap(dpi=150)
            pix.save(str(preview_path))
            return str(preview_path)
    except Exception:
        pass

    # High-quality visual synthetic render for PDF documents if fitz isn't installed
    # Read text lines if available
    canvas_w, canvas_h = 850, 1100
    img = Image.new("RGB", (canvas_w, canvas_h), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    # Draw simulated page header & decorative lines
    draw.rectangle([40, 40, canvas_w - 40, canvas_h - 40], outline="#E2E8F0", width=2)
    draw.rectangle([60, 60, canvas_w - 60, 110], fill="#F8FAFC")
    draw.text((80, 75), f"DocuMind AI Preview: {Path(file_path).name}", fill="#0F172A")
    draw.line([60, 120, canvas_w - 60, 120], fill="#E2E8F0", width=1)

    # Read binary or text snippet from file
    sample_text = ""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            sample_text = f.read(3000)
    except Exception:
        sample_text = "Binary Document Content"

    # Clean printable lines
    printable_lines = [line.strip() for line in sample_text.splitlines() if len(line.strip()) > 3]
    y_cursor = 150
    for line in printable_lines[:35]:
        clean_line = "".join(ch for ch in line if ch.isprintable())[:80]
        if clean_line:
            draw.text((80, y_cursor), clean_line, fill="#334155")
            y_cursor += 24
            if y_cursor > canvas_h - 100:
                break

    img.save(str(preview_path), "PNG")
    return str(preview_path)
