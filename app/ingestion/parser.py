from __future__ import annotations

from pathlib import Path
import re
from uuid import uuid4

import pdfplumber

from app.ingestion.extractors import extract_fields
from app.schemas.documents import DocumentChunk, ProcessedDocument
from app.services.docling_parser import parse_with_docling
from app.services.ocr import run_image_ocr


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


def parse_pdf(path: Path) -> tuple[str, list[DocumentChunk]]:
    docling_text = parse_with_docling(path)
    parts: list[str] = []
    chunks: list[DocumentChunk] = []
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                clean_text = _normalize_whitespace(text)
                parts.append(f"[Page {page_number}]\n{clean_text}")
                chunks.extend(
                    chunk_text(
                        clean_text,
                        page=page_number,
                        prefix=f"page-{page_number}",
                    )
                )

    fallback_text = "\n\n".join(parts)
    if fallback_text.strip():
        return fallback_text, chunks

    if docling_text.strip():
        return docling_text, chunk_text(docling_text)

    return "", []


def parse_image(path: Path) -> tuple[str, list[DocumentChunk]]:
    docling_text = parse_with_docling(path)
    if docling_text.strip():
        return docling_text, chunk_text(docling_text, page=1, prefix="image")

    ocr_text = run_image_ocr(path)
    if ocr_text.strip():
        normalized = _normalize_whitespace(ocr_text)
        return normalized, chunk_text(normalized, page=1, prefix="image")

    message = f"OCR could not extract text from {path.name}. Install Docling and PaddleOCR to enable full image parsing."
    return message, chunk_text(message, page=1, prefix="image")


def parse_document(path: Path) -> ProcessedDocument:
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
        filename=path.name,
        file_type=file_type,
        text=text,
        chunks=chunks,
        extracted_fields=extracted_fields,
    )
