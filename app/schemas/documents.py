from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    text: str
    page: int | None = None


class ExtractedFields(BaseModel):
    document_type: str = "Unknown"
    parties: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    key_obligations: list[str] = Field(default_factory=list)
    summary: str = ""


class ProcessedDocument(BaseModel):
    document_id: str
    filename: str
    file_type: str
    text: str
    chunks: list[DocumentChunk] = Field(default_factory=list)
    extracted_fields: ExtractedFields = Field(default_factory=ExtractedFields)


class WorkspaceQuery(BaseModel):
    question: str


class Citation(BaseModel):
    document_id: str
    filename: str
    page: int | None = None
    excerpt: str
    confidence: float | None = None


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)
