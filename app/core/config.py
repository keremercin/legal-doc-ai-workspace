from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
DEMO_DOCS_DIR = DATA_DIR / "demo_docs"
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def ensure_dirs() -> None:
    for path in (DATA_DIR, UPLOAD_DIR, PROCESSED_DIR, DEMO_DOCS_DIR):
        path.mkdir(parents=True, exist_ok=True)
