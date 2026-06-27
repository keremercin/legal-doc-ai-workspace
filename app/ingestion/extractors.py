from __future__ import annotations

import re
from collections import Counter

from app.schemas.documents import DocumentChunk, ExtractedFields


DATE_PATTERNS = [
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    r"\b\d{4}-\d{2}-\d{2}\b",
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}\b",
]


def detect_document_type(text: str) -> str:
    lowered = text.lower()
    if "amendment" in lowered:
        return "Amendment"
    if "non-disclosure agreement" in lowered or "nda" in lowered:
        return "Non-Disclosure Agreement"
    if "service agreement" in lowered:
        return "Service Agreement"
    if "employment agreement" in lowered:
        return "Employment Agreement"
    if "agreement" in lowered:
        return "Agreement"
    if "contract" in lowered:
        return "Contract"
    return "Unknown"


def extract_dates(text: str) -> list[str]:
    results: list[str] = []
    for pattern in DATE_PATTERNS:
        results.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    seen = []
    for item in results:
        if item not in seen:
            seen.append(item)
    return seen[:10]


def extract_parties(text: str) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    candidates: list[str] = []
    for line in lines[:80]:
        if any(keyword in line.lower() for keyword in ["between", "by and between", "party", "client", "provider"]):
            candidates.append(line)
    if not candidates:
        matches = re.findall(r"\b[A-Z][A-Za-z0-9&.,\- ]{2,60}(?:LLC|Inc\.|Ltd\.|Corporation|Company|Group)\b", text)
        candidates.extend(matches[:5])
    cleaned = []
    for item in candidates:
        compact = " ".join(item.split())
        if compact not in cleaned:
            cleaned.append(compact)
    return cleaned[:5]


def extract_key_obligations(chunks: list[DocumentChunk]) -> list[str]:
    signals = ("shall", "must", "agrees to", "is required to", "obligation", "deliver", "payment")
    hits: list[str] = []
    for chunk in chunks:
        sentences = re.split(r"(?<=[.!?])\s+", chunk.text)
        for sentence in sentences:
            if any(signal in sentence.lower() for signal in signals):
                sentence = " ".join(sentence.split())
                if 20 <= len(sentence) <= 300:
                    hits.append(sentence)
    ranked = Counter(hits)
    return [item for item, _ in ranked.most_common(5)]


def summarize_text(text: str) -> str:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not sentences:
        return ""
    return " ".join(sentences[:3])[:700]


def extract_fields(text: str, chunks: list[DocumentChunk]) -> ExtractedFields:
    return ExtractedFields(
        document_type=detect_document_type(text),
        parties=extract_parties(text),
        dates=extract_dates(text),
        key_obligations=extract_key_obligations(chunks),
        summary=summarize_text(text),
    )
