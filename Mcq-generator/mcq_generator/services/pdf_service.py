"""
PDF Service — extracts clean text from an uploaded PDF file.

Strategy:
  1. Try PyMuPDF (fitz) first — fast, handles most PDFs well.
  2. Fall back to pdfplumber — better for table-heavy / scanned-like PDFs.
  3. If both fail, raise a clear error for the UI to display.

No RAG needed: we extract ALL text and pass it directly to the LLM.
Groq's llama3-8b-8192 supports up to 8192 tokens (~6000 words).
For large PDFs we smart-truncate to stay within limits.
"""
import io
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Max characters we send to the LLM (~6000 words ≈ safe for 8192 token window)
MAX_CHARS = 12_000


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract and clean text from PDF bytes.

    Args:
        file_bytes: Raw bytes of the uploaded PDF file.

    Returns:
        Cleaned text string ready for MCQ generation.

    Raises:
        ValueError: If no readable text could be extracted.
    """
    text = _try_pymupdf(file_bytes)

    if not text or len(text.strip()) < 100:
        logger.info("PyMuPDF returned little text, trying pdfplumber...")
        text = _try_pdfplumber(file_bytes)

    if not text or len(text.strip()) < 100:
        raise ValueError(
            "Could not extract readable text from this PDF. "
            "The file may be scanned/image-based (no OCR support), "
            "password-protected, or corrupted."
        )

    cleaned = _clean_text(text)

    # Smart truncation: keep first MAX_CHARS characters
    if len(cleaned) > MAX_CHARS:
        logger.warning(
            "PDF text (%d chars) exceeds limit (%d), truncating.",
            len(cleaned),
            MAX_CHARS,
        )
        cleaned = cleaned[:MAX_CHARS]
        # Don't cut mid-sentence
        last_period = cleaned.rfind(".")
        if last_period > MAX_CHARS * 0.8:
            cleaned = cleaned[: last_period + 1]
        cleaned += "\n\n[Note: Content truncated to fit context window.]"

    return cleaned


def get_pdf_metadata(file_bytes: bytes) -> dict:
    """Return basic PDF metadata (page count, title if available)."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        meta = doc.metadata or {}
        return {
            "pages": doc.page_count,
            "title": meta.get("title", "").strip() or None,
            "author": meta.get("author", "").strip() or None,
        }
    except Exception:
        return {"pages": "?", "title": None, "author": None}


# ── Private helpers ───────────────────────────────────────────────────────────

def _try_pymupdf(file_bytes: bytes) -> Optional[str]:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text("text"))
        return "\n\n".join(pages_text)
    except ImportError:
        logger.warning("PyMuPDF not installed, skipping.")
        return None
    except Exception as e:
        logger.warning("PyMuPDF failed: %s", e)
        return None


def _try_pdfplumber(file_bytes: bytes) -> Optional[str]:
    try:
        import pdfplumber
        pages_text = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    pages_text.append(t)
        return "\n\n".join(pages_text)
    except ImportError:
        logger.warning("pdfplumber not installed, skipping.")
        return None
    except Exception as e:
        logger.warning("pdfplumber failed: %s", e)
        return None


def _clean_text(text: str) -> str:
    """Remove junk characters, excessive whitespace, and common PDF artefacts."""
    import re

    # Remove null bytes and form feeds
    text = text.replace("\x00", "").replace("\x0c", "\n")

    # Collapse 3+ newlines → 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove lines that are just page numbers or single characters
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip lone numbers (page numbers), empty lines between paragraphs
        if re.fullmatch(r"\d{1,4}", stripped):
            continue
        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()
