from __future__ import annotations

from pathlib import Path
import re
import tempfile
from uuid import uuid4

import pdfplumber

from app.ingestion.extractors import extract_fields
from app.schemas.documents import DocumentChunk, ProcessedDocument
from app.services.docling_parser import parse_with_docling
from app.services.ocr import run_image_ocr


class ExtractionError(RuntimeError):
    """Raised when a source document could not be read into searchable text."""


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150, page: int | None = None, prefix: str = "chunk") -> list[DocumentChunk]:
    if not text.strip():
        return []

    chunks: list[DocumentChunk] = []
    start = 0
    index = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk_text_value = text[start:end].strip()
        if chunk_text_value:
            chunks.append(
                DocumentChunk(
                    chunk_id=f"{prefix}-{index}",
                    text=chunk_text_value,
                    page=page,
                )
            )
            index += 1
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).strip()


def _extract_scanned_pdf_page(path: Path, page_number: int, page) -> str:
    """Extract one scan page through Docling, then local OCR as a fallback."""
    try:
        from pypdf import PdfReader, PdfWriter

        with tempfile.TemporaryDirectory(prefix="legal-doc-page-") as directory:
            reader = PdfReader(str(path))
            writer = PdfWriter()
            writer.add_page(reader.pages[page_number - 1])
            page_path = Path(directory) / f"page-{page_number}.pdf"
            with page_path.open("wb") as output:
                writer.write(output)
            docling_text = parse_with_docling(page_path)
            if docling_text.strip():
                return docling_text
    except Exception:
        # Try the page-image OCR adapter below; failure is surfaced by parse_pdf.
        pass

    try:
        with tempfile.TemporaryDirectory(prefix="legal-doc-ocr-") as directory:
            image_path = Path(directory) / f"page-{page_number}.png"
            page.to_image(resolution=180).save(image_path, format="PNG")
            return run_image_ocr(image_path)
    except Exception:
        return ""


def parse_pdf(path: Path) -> tuple[str, list[DocumentChunk]]:
    parts: list[str] = []
    chunks: list[DocumentChunk] = []
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                text = _extract_scanned_pdf_page(path, page_number, page)
            if not text.strip():
                raise ExtractionError(f"Could not extract text from PDF page {page_number}.")
            clean_text = _normalize_whitespace(text)
            parts.append(f"[Page {page_number}]\n{clean_text}")
            chunks.extend(
                chunk_text(
                    clean_text,
                    page=page_number,
                    prefix=f"page-{page_number}",
                )
            )

    return "\n\n".join(parts), chunks


def parse_image(path: Path) -> tuple[str, list[DocumentChunk]]:
    docling_text = parse_with_docling(path)
    if docling_text.strip():
        return docling_text, chunk_text(docling_text, page=1, prefix="image")

    ocr_text = run_image_ocr(path)
    if ocr_text.strip():
        normalized = _normalize_whitespace(ocr_text)
        return normalized, chunk_text(normalized, page=1, prefix="image")

    raise ExtractionError(f"OCR could not extract text from {path.name}.")


def parse_document(path: Path, display_filename: str | None = None) -> ProcessedDocument:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text, chunks = parse_pdf(path)
        file_type = "pdf"
    else:
        text, chunks = parse_image(path)
        file_type = "image"

    extracted_fields = extract_fields(text, chunks)

    return ProcessedDocument(
        document_id=str(uuid4()),
        filename=display_filename or path.name,
        file_type=file_type,
        text=text,
        chunks=chunks,
        extracted_fields=extracted_fields,
    )
