import asyncio
from pathlib import Path
import re
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import MAX_UPLOAD_BYTES, UPLOAD_DIR, ensure_dirs
from app.ingestion.parser import ExtractionError, parse_document
from app.retrieval.qa import answer_question
from app.schemas.documents import ProcessedDocument, QueryResponse, WorkspaceQuery
from app.services.storage import append_workspace_documents, load_workspace, reset_workspace

router = APIRouter()
_workspace_request_lock = asyncio.Lock()


def _safe_display_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    basename = filename.replace("\\", "/").rsplit("/", 1)[-1]
    suffix = Path(basename).suffix.lower()
    if suffix not in {".pdf", ".png", ".jpg", ".jpeg"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(basename).stem).strip("._-")[:80]
    if not stem:
        raise HTTPException(status_code=400, detail="Filename is invalid")
    return f"{stem}{suffix}"


@router.get("/")
def root() -> dict[str, str]:
    return {"message": "Legal Doc AI Pipeline API"}


@router.get("/workspace", response_model=list[ProcessedDocument])
def get_workspace() -> list[ProcessedDocument]:
    return load_workspace()


@router.post("/upload", response_model=list[ProcessedDocument])
async def upload_documents(files: list[UploadFile] = File(...)) -> list[ProcessedDocument]:
    async with _workspace_request_lock:
        ensure_dirs()
        documents: list[ProcessedDocument] = []
        written_paths: list[Path] = []
        try:
            for file in files:
                display_filename = _safe_display_filename(file.filename)
                content = await file.read(MAX_UPLOAD_BYTES + 1)
                if len(content) > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="File exceeds the 10 MiB upload limit")

                root = Path(UPLOAD_DIR).resolve()
                target = root / f"{uuid4().hex}-{display_filename}"
                if target.resolve().parent != root:
                    raise HTTPException(status_code=400, detail="Upload target is invalid")
                target.write_bytes(content)
                written_paths.append(target)
                try:
                    documents.append(parse_document(target, display_filename=display_filename))
                except ExtractionError as exc:
                    raise HTTPException(
                        status_code=422,
                        detail={"code": "EXTRACTION_ERROR", "message": str(exc)},
                    ) from exc

            return append_workspace_documents(documents)
        except Exception:
            for path in written_paths:
                try:
                    path.unlink()
                except FileNotFoundError:
                    pass
            raise


@router.post("/query", response_model=QueryResponse)
def query_workspace(payload: WorkspaceQuery) -> QueryResponse:
    return answer_question(payload.question, load_workspace())


@router.post("/reset")
async def clear_workspace() -> dict[str, str]:
    async with _workspace_request_lock:
        reset_workspace()
        return {"status": "reset"}
