"""Local OCR text extraction (PRD §7.5): receipt/statement image bytes are processed
entirely within this process and are never written to disk or sent to any third
party. Only the plain text this module returns is eligible to leave the process
(via ai_structuring_service)."""

import io

import pillow_heif
import pymupdf
import pytesseract
from fastapi import HTTPException, status
from PIL import Image

pillow_heif.register_heif_opener()

# Client-supplied Content-Type is only used for a fast, friendly early rejection —
# the actual PDF-vs-image parsing decision below is made from the file's magic
# bytes, since the header is attacker-controlled and cannot be trusted to route
# untrusted bytes into the right parser.
SUPPORTED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/heic",
    "image/heif",
    "application/pdf",
}
_MIN_EXTRACTED_TEXT_LENGTH = 10
_PDF_MAGIC = b"%PDF-"
_PDF_RENDER_DPI = 300
_PDF_MAX_RENDERED_PIXELS = 40_000_000  # ~40MP — generous for a scanned page, bounds worst-case allocation


def _load_pdf_page_as_image(file_bytes: bytes) -> Image.Image:
    try:
        with pymupdf.open(stream=file_bytes, filetype="pdf") as doc:
            if doc.page_count != 1:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Only single-page PDFs are supported — enter this transaction manually",
                )
            page = doc[0]
            rendered_width = page.rect.width / 72 * _PDF_RENDER_DPI
            rendered_height = page.rect.height / 72 * _PDF_RENDER_DPI
            if rendered_width * rendered_height > _PDF_MAX_RENDERED_PIXELS:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="PDF page is too large to process — enter this transaction manually",
                )
            pixmap = page.get_pixmap(dpi=_PDF_RENDER_DPI)
            return Image.open(io.BytesIO(pixmap.tobytes("png")))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to read the uploaded PDF — enter this transaction manually",
        ) from exc


def _load_image(file_bytes: bytes) -> Image.Image:
    if file_bytes.startswith(_PDF_MAGIC):
        return _load_pdf_page_as_image(file_bytes)
    try:
        return Image.open(io.BytesIO(file_bytes))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to read the uploaded file — enter this transaction manually",
        ) from exc


def extract_text(file_bytes: bytes, content_type: str) -> str:
    """Blocking (shells out to the tesseract binary) — call via asyncio.to_thread
    from an async route so it doesn't stall the event loop."""
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type — use jpg, png, heic, or a single-page PDF",
        )
    image = _load_image(file_bytes)
    text = pytesseract.image_to_string(image)
    if len(text.strip()) < _MIN_EXTRACTED_TEXT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not read text from this receipt — try a clearer photo or enter it manually",
        )
    return text
