import json
from pathlib import Path

import requests
from PIL import Image, ImageDraw


API = "http://127.0.0.1:8000"


def post_json(path: str, payload: dict | None = None) -> dict:
    response = requests.post(f"{API}{path}", json=payload or {}, timeout=60)
    response.raise_for_status()
    return response.json()


def get_json(path: str):
    response = requests.get(f"{API}{path}", timeout=60)
    response.raise_for_status()
    return response.json()


def upload_demo_files() -> list[dict]:
    files = []
    handles = []
    for pdf_path in sorted(Path("data/demo_docs").glob("*.pdf")):
        handle = pdf_path.open("rb")
        handles.append(handle)
        files.append(("files", (pdf_path.name, handle, "application/pdf")))

    response = requests.post(f"{API}/upload", files=files, timeout=120)
    for handle in handles:
        handle.close()
    response.raise_for_status()
    return response.json()


def create_image_demo() -> Path:
    path = Path("data/demo_docs/sample-ocr-image.png")
    img = Image.new("RGB", (1200, 350), color="white")
    draw = ImageDraw.Draw(img)
    lines = [
        "NON-DISCLOSURE AGREEMENT",
        "Effective Date: February 2, 2026",
        "Confidential materials must be returned within 10 business days upon request.",
    ]
    y = 40
    for line in lines:
        draw.text((40, y), line, fill="black")
        y += 80
    img.save(path)
    return path


def upload_single_file(path: Path) -> list[dict]:
    with path.open("rb") as handle:
        response = requests.post(
            f"{API}/upload",
            files={"files": (path.name, handle, "image/png")},
            timeout=120,
        )
    response.raise_for_status()
    return response.json()


def assert_true(name: str, condition: bool, details: str) -> dict:
    return {
        "name": name,
        "passed": bool(condition),
        "details": details,
    }


def main() -> None:
    results = []

    health = get_json("/health")
    results.append(assert_true("health_endpoint", health.get("status") == "ok", json.dumps(health)))

    reset = post_json("/reset")
    results.append(assert_true("reset_endpoint", reset.get("status") == "reset", json.dumps(reset)))

    uploaded = upload_demo_files()
    results.append(assert_true("upload_count", len(uploaded) == 3, f"uploaded={len(uploaded)}"))

    workspace = get_json("/workspace")
    results.append(assert_true("workspace_count", len(workspace) == 3, f"workspace={len(workspace)}"))

    doc_types = {item["extracted_fields"]["document_type"] for item in workspace}
    results.append(
        assert_true(
            "document_types_detected",
            {"Amendment", "Non-Disclosure Agreement", "Service Agreement"}.issubset(doc_types),
            f"types={sorted(doc_types)}",
        )
    )

    total_dates = sum(len(item["extracted_fields"]["dates"]) for item in workspace)
    results.append(assert_true("date_extraction", total_dates >= 4, f"dates={total_dates}"))

    total_obligations = sum(len(item["extracted_fields"]["key_obligations"]) for item in workspace)
    results.append(assert_true("obligation_extraction", total_obligations >= 8, f"obligations={total_obligations}"))

    query_one = post_json(
        "/query",
        {"question": "What changed in the amendment and what confidentiality obligations exist?"},
    )
    results.append(
        assert_true(
            "multi_doc_query",
            len(query_one.get("citations", [])) >= 2,
            f"citations={len(query_one.get('citations', []))}",
        )
    )

    query_two = post_json(
        "/query",
        {"question": "What is the payment term in the service agreement?"},
    )
    answer_two = query_two.get("answer", "").lower()
    results.append(
        assert_true(
            "service_agreement_query",
            "15 days" in answer_two or len(query_two.get("citations", [])) >= 1,
            query_two.get("answer", "")[:220],
        )
    )

    query_three = post_json(
        "/query",
        {"question": "When does the confidentiality obligation survive until?"},
    )
    answer_three = query_three.get("answer", "").lower()
    results.append(
        assert_true(
            "nda_query",
            "24 months" in answer_three or len(query_three.get("citations", [])) >= 1,
            query_three.get("answer", "")[:220],
        )
    )

    image_path = create_image_demo()
    image_result = upload_single_file(image_path)
    image_doc = next((doc for doc in image_result if doc["filename"].endswith(image_path.name)), None)
    image_text = (image_doc or {}).get("text", "")
    results.append(
        assert_true(
            "image_ingestion_path",
            image_doc is not None,
            f"image_doc_found={image_doc is not None}",
        )
    )
    results.append(
        assert_true(
            "image_text_extraction",
            "confidential" in image_text.lower() or "ocr could not extract text" in image_text.lower(),
            image_text[:220],
        )
    )

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
