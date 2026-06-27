from __future__ import annotations

from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def get_docling_converter():
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption
    except Exception:
        return None

    try:
        pdf_options = PdfPipelineOptions()
        pdf_options.do_ocr = True
        pdf_options.do_table_structure = True

        return DocumentConverter(
            allowed_formats=[InputFormat.PDF, InputFormat.IMAGE],
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
            },
        )
    except Exception:
        try:
            return DocumentConverter()
        except Exception:
            return None


def parse_with_docling(path: Path) -> str:
    converter = get_docling_converter()
    if converter is None:
        return ""

    try:
        result = converter.convert(str(path))
        document = getattr(result, "document", None)
        if document is None:
            return ""

        for method_name in ("export_to_markdown", "render_as_markdown"):
            method = getattr(document, method_name, None)
            if callable(method):
                text = method()
                if isinstance(text, str) and text.strip():
                    return text
    except Exception:
        return ""

    return ""
