from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import threading
from collections.abc import Iterator
from contextlib import contextmanager

from app.core.config import PROCESSED_DIR, ensure_dirs
from app.schemas.documents import ProcessedDocument


WORKSPACE_FILE = PROCESSED_DIR / "workspace.json"
_LOCAL_LOCK = threading.RLock()


@contextmanager
def _workspace_lock() -> Iterator[None]:
    ensure_dirs()
    lock_path = WORKSPACE_FILE.with_suffix(".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with _LOCAL_LOCK, lock_path.open("a+b") as lock_file:
        lock_file.seek(0, os.SEEK_END)
        if lock_file.tell() == 0:
            lock_file.write(b"0")
            lock_file.flush()
        lock_file.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _load_unlocked() -> list[ProcessedDocument]:
    if not WORKSPACE_FILE.exists():
        return []
    data = json.loads(WORKSPACE_FILE.read_text(encoding="utf-8"))
    return [ProcessedDocument.model_validate(item) for item in data]


def _save_unlocked(documents: list[ProcessedDocument]) -> None:
    WORKSPACE_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = [doc.model_dump() for doc in documents]
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=WORKSPACE_FILE.parent,
            prefix=f".{WORKSPACE_FILE.name}.", suffix=".tmp", delete=False,
        ) as output:
            temporary_path = Path(output.name)
            json.dump(payload, output, ensure_ascii=False, indent=2)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_path, WORKSPACE_FILE)
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()


def load_workspace() -> list[ProcessedDocument]:
    with _workspace_lock():
        return _load_unlocked()


def save_workspace(documents: list[ProcessedDocument]) -> None:
    with _workspace_lock():
        _save_unlocked(documents)


def append_workspace_documents(documents: list[ProcessedDocument]) -> list[ProcessedDocument]:
    with _workspace_lock():
        current = _load_unlocked()
        current.extend(documents)
        _save_unlocked(current)
        return current


def reset_workspace() -> None:
    with _workspace_lock():
        # Reset the searchable workspace index; source uploads remain available to the owner.
        _save_unlocked([])
