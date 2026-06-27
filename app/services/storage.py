from __future__ import annotations

import json
from pathlib import Path

from app.core.config import PROCESSED_DIR, ensure_dirs
from app.schemas.documents import ProcessedDocument


WORKSPACE_FILE = PROCESSED_DIR / "workspace.json"


def load_workspace() -> list[ProcessedDocument]:
    ensure_dirs()
    if not WORKSPACE_FILE.exists():
        return []
    data = json.loads(WORKSPACE_FILE.read_text(encoding="utf-8"))
    return [ProcessedDocument.model_validate(item) for item in data]


def save_workspace(documents: list[ProcessedDocument]) -> None:
    ensure_dirs()
    payload = [doc.model_dump() for doc in documents]
    WORKSPACE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def reset_workspace() -> None:
    ensure_dirs()
    if WORKSPACE_FILE.exists():
        WORKSPACE_FILE.unlink()
