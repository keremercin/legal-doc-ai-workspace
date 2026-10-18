from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api import routes
from app.core import config
from app.main import app
from app.retrieval.qa import answer_question
from app.schemas.documents import DocumentChunk, ExtractedFields, ProcessedDocument
from app.services import storage
from app.ingestion import parser
from app.ingestion.parser import ExtractionError


def _document(document_id: str, filename: str = "source.pdf") -> ProcessedDocument:
    chunk = DocumentChunk(chunk_id=f"{document_id}-1", text="The agreement requires payment within 15 days.", page=2)
    return ProcessedDocument(
        document_id=document_id,
        filename=filename,
        file_type="pdf",
        text=chunk.text,
        chunks=[chunk],
        extracted_fields=ExtractedFields(document_type="Agreement"),
    )


def test_failed_image_ocr_raises_extraction_error_not_searchable_text(tmp_path, monkeypatch):
    monkeypatch.setattr(parser, "parse_with_docling", lambda _path: "")
    monkeypatch.setattr(parser, "run_image_ocr", lambda _path: "")

    with pytest.raises(ExtractionError, match="OCR could not extract"):
        parser.parse_image(tmp_path / "scan.png")


def test_mixed_pdf_keeps_text_layer_and_extracts_empty_page(tmp_path, monkeypatch):
    class Page:
        def __init__(self, text):
            self.text = text

        def extract_text(self):
            return self.text

    class Pdf:
        pages = [Page("Text layer page"), Page("")]

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

    fallback_calls = []
    monkeypatch.setattr(parser.pdfplumber, "open", lambda _path: Pdf())
    monkeypatch.setattr(
        parser,
        "_extract_scanned_pdf_page",
        lambda _path, page_number, _page: fallback_calls.append(page_number) or "Scanned page text",
        raising=False,
    )

    text, chunks = parser.parse_pdf(tmp_path / "mixed.pdf")

    assert "Text layer page" in text
    assert "Scanned page text" in text
    assert fallback_calls == [2]
    assert [chunk.page for chunk in chunks] == [1, 2]


def test_citation_keeps_document_and_page_source_with_heuristic_score():
    result = answer_question("What are the payment terms?", [_document("doc-1", "contract.pdf")])

    citation = result.citations[0]
    assert citation.document_id == "doc-1"
    assert citation.filename == "contract.pdf"
    assert citation.page == 2
    assert "payment within 15 days" in citation.excerpt
    assert 0.0 <= citation.rank_score <= 1.0
    assert not hasattr(citation, "confidence")


def test_upload_sanitizes_filename_and_writes_under_upload_root(tmp_path, monkeypatch):
    upload_dir = tmp_path / "uploads"
    workspace_file = tmp_path / "processed" / "workspace.json"
    seen_paths: list[Path] = []
    monkeypatch.setattr(routes, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(config, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(storage, "WORKSPACE_FILE", workspace_file)

    def parse(path: Path, display_filename: str | None = None):
        seen_paths.append(path)
        return _document("uploaded", display_filename or path.name)

    monkeypatch.setattr(routes, "parse_document", parse)
    response = TestClient(app).post(
        "/upload",
        files=[("files", (r"..\..\outside.pdf", b"pdf bytes", "application/pdf"))],
    )

    assert response.status_code == 200
    assert len(seen_paths) == 1
    assert seen_paths[0].resolve().parent == upload_dir.resolve()
    assert seen_paths[0].is_file()
    assert response.json()[0]["filename"] == "outside.pdf"


def test_upload_rejects_large_file_without_saving_or_ingesting(tmp_path, monkeypatch):
    upload_dir = tmp_path / "uploads"
    workspace_file = tmp_path / "processed" / "workspace.json"
    monkeypatch.setattr(routes, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(config, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(routes, "MAX_UPLOAD_BYTES", 4, raising=False)
    monkeypatch.setattr(storage, "WORKSPACE_FILE", workspace_file)
    monkeypatch.setattr(routes, "parse_document", lambda *_args, **_kwargs: pytest.fail("oversize input was parsed"))

    response = TestClient(app).post("/upload", files=[("files", ("large.pdf", b"12345", "application/pdf"))])

    assert response.status_code == 413
    assert storage.load_workspace() == []
    assert not list(upload_dir.glob("*"))


def test_extraction_error_does_not_save_searchable_error_document(tmp_path, monkeypatch):
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(routes, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(config, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(storage, "WORKSPACE_FILE", tmp_path / "workspace.json")
    monkeypatch.setattr(routes, "parse_document", lambda *_args, **_kwargs: (_ for _ in ()).throw(ExtractionError("OCR could not extract text")))

    response = TestClient(app).post("/upload", files=[("files", ("scan.png", b"image", "image/png"))])

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "EXTRACTION_ERROR"
    assert storage.load_workspace() == []
    assert not list(upload_dir.glob("*"))


def test_reset_clears_workspace_without_deleting_uploaded_files(tmp_path, monkeypatch):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    managed_upload = upload_dir / "0123456789abcdef0123456789abcdef-contract.pdf"
    sentinel = upload_dir / "keep-me.txt"
    managed_upload.write_bytes(b"uploaded content")
    sentinel.write_text("preserve", encoding="utf-8")
    monkeypatch.setattr(routes, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(storage, "WORKSPACE_FILE", tmp_path / "workspace.json")
    storage.save_workspace([_document("doc-1")])

    client = TestClient(app)
    assert client.post("/reset").status_code == 200

    assert client.get("/workspace").json() == []
    assert managed_upload.read_bytes() == b"uploaded content"
    assert sentinel.read_text(encoding="utf-8") == "preserve"


def test_concurrent_workspace_appends_do_not_lose_updates(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "WORKSPACE_FILE", tmp_path / "workspace.json")
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(lambda n: storage.append_workspace_documents([_document(f"doc-{n}")]), range(20)))

    documents = storage.load_workspace()
    assert len(documents) == 20
    assert {document.document_id for document in documents} == {f"doc-{n}" for n in range(20)}
