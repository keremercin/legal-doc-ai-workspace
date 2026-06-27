from __future__ import annotations

from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def get_paddle_ocr():
    try:
        from paddleocr import PaddleOCR
    except Exception:
        return None

    try:
        return PaddleOCR(
            lang="en",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
    except Exception:
        return None


@lru_cache(maxsize=1)
def get_rapid_ocr():
    try:
        from rapidocr import RapidOCR
    except Exception:
        return None

    try:
        return RapidOCR()
    except Exception:
        return None


def _flatten_ocr_result(result) -> str:
    parts: list[str] = []

    if isinstance(result, list):
        for item in result:
            parts.append(_flatten_ocr_result(item))
        return "\n".join(part for part in parts if part).strip()

    items = getattr(result, "items", None)
    if items:
        for item in items:
            text = getattr(item, "text", None)
            if text:
                parts.append(str(text))
        if parts:
            return "\n".join(parts).strip()

    rec_texts = getattr(result, "rec_texts", None)
    if rec_texts:
        parts.extend(str(text) for text in rec_texts if text)
        return "\n".join(parts).strip()

    data = getattr(result, "data", None)
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))
        if parts:
            return "\n".join(parts).strip()

    return ""


def run_image_ocr(path: Path) -> str:
    ocr = get_paddle_ocr()
    if ocr is not None:
        try:
            result = ocr.predict(str(path))
            text = _flatten_ocr_result(result)
            if text.strip():
                return text
        except Exception:
            pass

    rapid_ocr = get_rapid_ocr()
    if rapid_ocr is not None:
        try:
            result = rapid_ocr(str(path))
            lines = []
            txts = getattr(result, "txts", None)
            if txts:
                lines.extend(str(item) for item in txts if item)
            elif result:
                try:
                    lines.extend(item[1] for item in result if len(item) > 1 and item[1])
                except Exception:
                    pass
            if lines:
                text = "\n".join(lines).strip()
                if text:
                    return text
        except Exception:
            pass

    return ""
