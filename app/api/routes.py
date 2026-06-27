from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile

from app.core.config import UPLOAD_DIR, ensure_dirs
from app.ingestion.parser import parse_document
from app.retrieval.qa import answer_question
from app.schemas.documents import ProcessedDocument, QueryResponse, WorkspaceQuery
from app.services.storage import load_workspace, reset_workspace, save_workspace

router = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    return {"message": "Legal Doc AI Pipeline API"}


@router.get("/workspace", response_model=list[ProcessedDocument])
def get_workspace() -> list[ProcessedDocument]:
    return load_workspace()


@router.post("/upload", response_model=list[ProcessedDocument])
async def upload_documents(files: list[UploadFile] = File(...)) -> list[ProcessedDocument]:
    ensure_dirs()
    current = load_workspace()

    for file in files:
        suffix = Path(file.filename).suffix.lower()
        if suffix not in {".pdf", ".png", ".jpg", ".jpeg"}:
            continue

        target = UPLOAD_DIR / f"{uuid4()}-{file.filename}"
        target.write_bytes(await file.read())
        current.append(parse_document(target))

    save_workspace(current)
    return current


@router.post("/query", response_model=QueryResponse)
def query_workspace(payload: WorkspaceQuery) -> QueryResponse:
    return answer_question(payload.question, load_workspace())


@router.post("/reset")
def clear_workspace() -> dict[str, str]:
    reset_workspace()
    return {"status": "reset"}
