from __future__ import annotations

import re
from collections import Counter

from app.schemas.documents import Citation, ProcessedDocument, QueryResponse


STOPWORDS = {
    "what", "which", "when", "where", "who", "why", "how", "the", "and", "for", "with", "that",
    "this", "from", "into", "does", "about", "have", "has", "will", "would", "there", "their",
    "them", "your", "across", "exist", "until",
}


def _tokenize(text: str) -> list[str]:
    return [
        token for token in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    ]


def _score_chunk(question_tokens: list[str], chunk_text: str, document: ProcessedDocument) -> float:
    chunk_tokens = _tokenize(chunk_text)
    if not chunk_tokens:
        return 0.0

    counter = Counter(chunk_tokens)
    score = 0.0
    for token in question_tokens:
        score += counter[token] * 2.0

    lowered = chunk_text.lower()
    question_text = " ".join(question_tokens)

    if "amendment" in question_text and "amendment" in lowered:
        score += 3.0
    if "confidential" in question_text and ("confidential" in lowered or "non-disclosure" in lowered):
        score += 3.0
    if "payment" in question_text and ("payment" in lowered or "invoice" in lowered):
        score += 2.5
    if "date" in question_text and any(word in lowered for word in ["effective", "dated", "term", "begins", "ends"]):
        score += 1.5

    doc_type = document.extracted_fields.document_type.lower()
    if "amendment" in question_text and "amendment" in doc_type:
        score += 2.0
    if ("nda" in question_text or "confidential" in question_text) and "non-disclosure" in doc_type:
        score += 2.0
    if "service agreement" in question_text and "service agreement" in doc_type:
        score += 2.0

    return score


def answer_question(question: str, documents: list[ProcessedDocument]) -> QueryResponse:
    lowered_question = question.lower().strip()
    if not lowered_question:
        return QueryResponse(answer="Ask a question about the uploaded documents.", citations=[])

    question_tokens = _tokenize(lowered_question)
    ranked: list[tuple[float, ProcessedDocument, str, int | None]] = []

    for document in documents:
        for chunk in document.chunks:
            score = _score_chunk(question_tokens, chunk.text, document)
            if score > 0:
                ranked.append((score, document, chunk.text[:320].strip(), chunk.page))

    ranked.sort(key=lambda item: item[0], reverse=True)

    if not ranked:
        return QueryResponse(
            answer="No strong answer found yet. The retrieval layer is active, but semantic ranking will be improved in the next iteration.",
            citations=[],
        )

    matches: list[Citation] = []
    snippets: list[str] = []
    seen_pairs: set[tuple[str, str]] = set()
    top_score = ranked[0][0]

    for score, document, excerpt, page in ranked:
        key = (document.document_id, excerpt)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        normalized_confidence = min(0.98, max(0.45, score / max(top_score, 1.0)))
        matches.append(
            Citation(
                document_id=document.document_id,
                filename=document.filename,
                page=page,
                excerpt=excerpt,
                confidence=round(normalized_confidence, 2),
            )
        )
        snippets.append(f"[{document.extracted_fields.document_type}] {excerpt}")
        if len(matches) >= 3:
            break

    answer = "Based on the uploaded documents, the strongest evidence is: " + " ".join(snippets[:2])
    return QueryResponse(answer=answer[:900], citations=matches)
