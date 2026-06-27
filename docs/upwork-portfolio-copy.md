# Upwork Portfolio Copy

## Portfolio Title

Legal Document AI Pipeline with OCR, Multi-Document Extraction and Grounded Q&A

## Short Description

Built a local-first legal document intelligence tool that ingests multiple files, extracts structured fields, identifies obligations, and answers cross-document questions with grounded citations.

## Long Case Study

### Overview

This project is a product-style legal document AI workspace designed for contract-heavy teams that need more than a simple summarizer.

The system supports multi-document ingestion, structured extraction, obligation discovery, and grounded Q&A across a shared workspace.

### Problem

Most document AI demos stop at single-file uploads and generic summaries. In real legal and operations workflows, teams need to:

- work across multiple related documents
- identify dates, parties, and obligations quickly
- compare documents such as agreements and amendments
- ask questions and see traceable evidence instead of opaque answers

### Solution

I built a local-first document intelligence pipeline with:

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

### Outcome

The result is a strong portfolio-ready prototype that demonstrates how AI can support legal review workflows in a more realistic way than a basic chatbot or OCR script.

It shows:

- multi-document reasoning
- legal-focused extraction
- grounded answer generation
- a clean internal-tool style interface

## Problem / Solution / Result Version

### Problem

Legal teams often work with related documents such as agreements, amendments, and NDAs, but most lightweight AI tools only handle one file at a time.

### Solution

I built a local-first legal document workspace that extracts key fields, identifies obligations, and answers cross-document questions using grounded source excerpts.

### Result

The demo shows a realistic internal tool workflow with multiple uploaded legal files, structured extraction, and citation-backed Q&A in one interface.
