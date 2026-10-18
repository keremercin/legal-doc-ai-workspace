# Legal Doc AI Workspace

Open-source local document-processing demo with heuristic extraction, lexical retrieval, and source excerpts.

This project is a local-first workspace reference implementation for contract and document operations. It is designed to feel like an internal tool rather than a single-file OCR demo.

## What It Does

- Upload multiple PDF or image documents (up to 10 MiB each) into a local workspace
- Parse documents into machine-readable text
- Extract legal metadata and key structured signals
- Surface obligations, dates, parties, and summaries
- Run workspace-level Q&A across multiple uploaded files
- Return grounded evidence snippets with source attribution

## Why This Exists

Many AI document demos stop at "upload a file and summarize it." Real document workflows need more:

- multiple documents, not single-file toys
- legal-friendly extraction, not generic text dumps
- local-first architecture, not API-only dependence
- traceable answers tied back to source evidence

This repository is designed to showcase exactly that direction.

## Screenshots

### Workspace Dashboard

![Workspace Dashboard](docs/screenshots/workspace-dashboard-clean.png)

### Multi-Document Q&A

![Multi-Document Q&A](docs/screenshots/multi-doc-qa-clean.png)

## Current Product Scope

The first release is focused on legal and contract-heavy workflows, with room to expand into:

- claims and compliance packs
- policy review
- procurement and vendor paperwork
- invoice and report ingestion
- internal document operations

## Current Features

- Multi-document workspace
- PDF ingestion and parsing
- Image-ready OCR integration layer
- Document type detection
- Parties extraction
- Dates extraction
- Key obligations extraction
- Short document summary generation
- Workspace Q&A with citation cards
- Product-style Streamlit UI for demo and portfolio use

## Example Workflow

1. Upload a service agreement, an amendment, and an NDA
2. Review extracted metadata for each document
3. Ask a cross-document question such as:
   `What changed in the amendment and what confidentiality obligations exist?`
4. Inspect the answer plus grounded source excerpts from more than one document

## Tech Stack

- `FastAPI` for backend APIs
- `Streamlit` for the demo application
- `Docling` integration layer for structured document parsing
- `PaddleOCR` integration layer for OCR fallback
- `pdfplumber` fallback for robust PDF text extraction
- `Pydantic` schemas for workspace and citation models

## Parsing Strategy

The parsing layer handles each PDF page independently:

- text-layer pages are read with `pdfplumber`
- blank/scanned pages are sent to Docling one page at a time, then to local OCR if needed
- if a page still cannot be extracted, upload stops with an explicit extraction error; the error text is never indexed as document content
- image parsing is structured to use `Docling` and `PaddleOCR`
- upload names are reduced to a safe basename and stored under generated local names
- workspace JSON updates are atomic and file-locked; `/reset` clears the searchable index but preserves uploaded source files
- citation `rank_score` is a normalized lexical heuristic for ordering, not a calibrated confidence percentage

This makes the demo more stable in local environments while keeping the architecture extensible.

## Project Structure

```text
legal-doc-ai-workspace/
  app/
    api/            # FastAPI routes
    core/           # shared config
    ingestion/      # parsing and extraction logic
    retrieval/      # Q&A and citation response logic
    schemas/        # Pydantic models
    services/       # storage, OCR, Docling adapters
  data/
    demo_docs/      # generated portfolio demo files
    processed/      # cached workspace state
    uploads/        # uploaded source files
  scripts/
    create_demo_pdf.py
    upload_demo.py
  ui/
    app.py          # Streamlit product UI
```

## Local Run

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the backend:

```bash
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Start the UI:

```bash
.venv\Scripts\python.exe -m streamlit run .\ui\app.py --server.address 127.0.0.1 --server.port 8501
```

Open:

- API: `http://127.0.0.1:8000`
- UI: `http://localhost:8501`

## Demo Data

This repo includes helper scripts to generate and upload demo legal documents:

```bash
.venv\Scripts\python.exe .\scripts\create_demo_pdf.py
.venv\Scripts\python.exe .\scripts\upload_demo.py
```

The generated workspace includes:

- a service agreement
- an amendment
- an NDA

## Automated Regression Tests

The current checkout suite has **9 passing tests** covering:

- OCR failure stops ingestion with an explicit error
- mixed text/scanned PDF page extraction
- citation document/page source metadata
- safe upload filenames and size limits
- reset clears the index while preserving uploaded files
- concurrent JSON updates and escaped HTML presentation

These tests do not validate live OCR quality or a browser deployment.

## Known Gaps

- citations carry page-level source metadata but do not highlight exact text coordinates
- semantic ranking is still basic and can be improved
- image OCR integrations need a dedicated live image validation pass
- the current demo uses generated documents rather than public legal datasets

## Next Improvements

- exact excerpt highlighting
- stronger retrieval ranking
- richer citation highlighting
- better document switching UX
- README screenshots and GIF demo

## Portfolio Positioning

This project is best positioned as:

`Local-first document-processing demo with heuristic extraction and lexical source search`
