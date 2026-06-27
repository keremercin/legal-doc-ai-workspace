import json
from pathlib import Path

import requests


def main() -> None:
    files = []
    handles = []
    for pdf_path in sorted(Path("data/demo_docs").glob("*.pdf")):
        handle = pdf_path.open("rb")
        handles.append(handle)
        files.append(("files", (pdf_path.name, handle, "application/pdf")))

    response = requests.post(
        "http://127.0.0.1:8000/upload",
        files=files,
        timeout=120,
    )

    for handle in handles:
        handle.close()

    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
    main()
