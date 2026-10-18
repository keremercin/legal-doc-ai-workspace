# Legal Document Workspace Demo Description

## Portfolio Title

Local Document Processing Prototype with Heuristic Retrieval and Source Excerpts

## Short Description

Built a local-first prototype that ingests PDFs/images, extracts text and heuristic fields, ranks chunks lexically, and returns excerpts with document/page source metadata. Its answers are not validated legal interpretations.

## Scope

### Overview

This is a portfolio demo, not a customer case study or deployed legal tool.

The system supports multi-document ingestion, heuristic field extraction, obligation sentence matching, and lexical Q&A over a shared local workspace.

### Problem

The demo illustrates how uploaded documents can be indexed locally and how matching excerpts are returned with source details.

### Solution

The code includes:

- multi-document workspace ingestion
- legal-oriented metadata extraction
- summary and obligation generation
- workspace-level Q&A
- citation cards with source evidence
- product-style review UI for fast navigation

### Stack

- FastAPI
- Streamlit
- Pydantic
- pdfplumber
- Docling integration layer
- PaddleOCR integration layer

### Demonstrated Behavior

It shows:

- lexical chunk ranking across uploaded documents
- legal-focused extraction
- source-linked excerpts
- a clean internal-tool style interface

No customer use, time savings, legal accuracy, AI quality rate, or business outcome has been measured.

## Short Description

The local demo displays multiple uploaded files, heuristic extracted fields, and source excerpts ranked by lexical overlap. It does not verify legal claims or represent client work.
