import requests
import streamlit as st


API_BASE = "http://127.0.0.1:8000"


def fetch_workspace() -> list[dict]:
    response = requests.get(f"{API_BASE}/workspace", timeout=30)
    response.raise_for_status()
    return response.json()


def upload_files(files) -> list[dict]:
    payload = [("files", (file.name, file.getvalue(), file.type or "application/octet-stream")) for file in files]
    response = requests.post(f"{API_BASE}/upload", files=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def run_query(question: str) -> dict:
    response = requests.post(f"{API_BASE}/query", json={"question": question}, timeout=60)
    response.raise_for_status()
    return response.json()


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(16, 185, 129, 0.09), transparent 24%),
                    radial-gradient(circle at top right, rgba(59, 130, 246, 0.05), transparent 22%),
                    linear-gradient(180deg, #f4f7f2 0%, #edf2ec 100%);
                color: #17201b;
            }
            .block-container {
                padding-top: 1.15rem;
                padding-bottom: 2rem;
                max-width: 1420px;
            }
            .hero {
                background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(249, 251, 248, 0.9));
                border: 1px solid rgba(20, 28, 23, 0.07);
                border-radius: 30px;
                padding: 1.25rem 1.35rem 1.1rem;
                box-shadow: 0 24px 60px rgba(15, 23, 18, 0.08);
                backdrop-filter: blur(10px);
                margin-bottom: 0.9rem;
            }
            .hero-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                margin-bottom: 1rem;
            }
            .brand {
                font-size: 1.85rem;
                font-weight: 700;
                letter-spacing: -0.03em;
                color: #122019;
            }
            .subtle {
                color: #5b6b63;
                font-size: 0.95rem;
                line-height: 1.5;
            }
            .badge-row {
                display: flex;
                gap: 0.55rem;
                flex-wrap: wrap;
                margin-top: 0.8rem;
            }
            .badge {
                background: #eef6ef;
                border: 1px solid #d7e6d9;
                color: #214a34;
                border-radius: 999px;
                padding: 0.42rem 0.76rem;
                font-size: 0.78rem;
                font-weight: 600;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.85rem;
                margin-top: 0.85rem;
            }
            .stat-card {
                background: rgba(255,255,255,0.96);
                border: 1px solid rgba(20, 28, 23, 0.07);
                border-radius: 22px;
                padding: 0.85rem 0.95rem;
            }
            .stat-label {
                font-size: 0.76rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: #738279;
                margin-bottom: 0.3rem;
            }
            .stat-value {
                font-size: 1.25rem;
                font-weight: 700;
                color: #122019;
            }
            .toolbar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
                margin: 0.25rem 0 0.9rem;
            }
            .toolbar-note {
                color: #6c7c73;
                font-size: 0.84rem;
            }
            .workspace-stack {
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }
            .section-title {
                font-size: 1.12rem;
                font-weight: 700;
                color: #16231c;
                margin-bottom: 0.2rem;
            }
            .section-copy {
                font-size: 0.92rem;
                color: #68786f;
                margin-bottom: 0.9rem;
            }
            .mini-card {
                background: rgba(255,255,255,0.94);
                border: 1px solid rgba(20, 28, 23, 0.08);
                border-radius: 20px;
                padding: 0.95rem 1rem;
                box-shadow: 0 12px 30px rgba(15, 23, 18, 0.04);
            }
            .mini-card.active {
                border-color: #bfd6c5;
                box-shadow: 0 14px 34px rgba(24, 66, 42, 0.08);
            }
            .file-title {
                font-size: 0.96rem;
                font-weight: 700;
                color: #17201b;
                margin-bottom: 0.15rem;
            }
            .file-meta {
                font-size: 0.82rem;
                color: #728279;
            }
            .status-row {
                display: flex;
                gap: 0.45rem;
                flex-wrap: wrap;
                margin-top: 0.55rem;
            }
            .status-pill {
                display: inline-block;
                background: #f3f7f3;
                border: 1px solid #dde7df;
                color: #375844;
                border-radius: 999px;
                padding: 0.18rem 0.5rem;
                font-size: 0.72rem;
                font-weight: 600;
            }
            .extract-card {
                background: rgba(255,255,255,0.95);
                border: 1px solid rgba(20, 28, 23, 0.08);
                border-radius: 24px;
                padding: 1.1rem 1.1rem 1rem;
                margin-bottom: 0.95rem;
                box-shadow: 0 16px 34px rgba(15, 23, 18, 0.055);
            }
            .extract-heading {
                font-size: 1.08rem;
                font-weight: 700;
                color: #17211b;
                margin-bottom: 0.15rem;
            }
            .extract-type {
                font-size: 0.82rem;
                color: #5d6d64;
                margin-bottom: 0.8rem;
            }
            .chip {
                display: inline-block;
                background: #f3f7f3;
                border: 1px solid #dde8df;
                color: #234332;
                border-radius: 999px;
                padding: 0.28rem 0.58rem;
                font-size: 0.76rem;
                margin-right: 0.35rem;
                margin-bottom: 0.35rem;
            }
            .answer-card {
                background: rgba(255,255,255,0.96);
                border: 1px solid rgba(20, 28, 23, 0.08);
                border-radius: 24px;
                padding: 1rem;
                margin-top: 0.8rem;
            }
            .answer-meta {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 0.8rem;
                margin-bottom: 0.65rem;
            }
            .answer-kicker {
                color: #6b7b72;
                font-size: 0.78rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                font-weight: 700;
            }
            .citation-card {
                background: #f7faf7;
                border: 1px solid #dfe8e1;
                border-radius: 16px;
                padding: 0.8rem 0.9rem;
                margin-top: 0.65rem;
            }
            .citation-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 0.5rem;
                margin-bottom: 0.4rem;
            }
            .citation-meta {
                color: #6f7f76;
                font-size: 0.75rem;
            }
            .confidence-pill {
                display: inline-block;
                background: #eaf5ee;
                color: #245338;
                border: 1px solid #d5e8da;
                border-radius: 999px;
                padding: 0.18rem 0.48rem;
                font-size: 0.7rem;
                font-weight: 700;
            }
            [data-testid="stFileUploader"] {
                background: linear-gradient(180deg, #1d2320 0%, #252c29 100%);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 22px;
                padding: 0.65rem;
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
            }
            [data-testid="stFileUploader"] section {
                padding: 0.4rem 0.5rem 0.2rem;
            }
            [data-testid="stFileUploader"] small,
            [data-testid="stFileUploader"] span,
            [data-testid="stFileUploader"] label,
            [data-testid="stFileUploader"] div {
                color: #dbe5de !important;
            }
            .stButton > button {
                width: 100%;
                border-radius: 16px;
                border: 1px solid #13291e;
                background: linear-gradient(180deg, #214e37 0%, #173727 100%);
                color: #f5fbf7;
                font-weight: 700;
                min-height: 2.9rem;
                box-shadow: 0 14px 30px rgba(23, 55, 39, 0.18);
            }
            .stButton > button:hover {
                border-color: #163624;
                background: linear-gradient(180deg, #276043 0%, #1a422e 100%);
                color: #ffffff;
            }
            .stTextArea textarea {
                background: #202522 !important;
                color: #edf5ef !important;
                border: 1px solid #313834 !important;
                border-radius: 18px !important;
                min-height: 150px !important;
            }
            [data-testid="stMetricValue"] {
                color: #102018 !important;
                font-weight: 700 !important;
            }
            [data-testid="stMetricLabel"] {
                color: #6c7c73 !important;
            }
            div[data-testid="stMetric"] {
                background: #f7faf7;
                border: 1px solid #e2eae4;
                padding: 0.7rem 0.85rem;
                border-radius: 16px;
            }
            div[data-testid="stAlert"] {
                border-radius: 16px;
            }
            @media (max-width: 1100px) {
                .stats-grid {
                    grid-template-columns: repeat(2, minmax(0, 1fr));
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(workspace: list[dict]) -> None:
    doc_count = len(workspace)
    chunk_count = sum(len(item.get("chunks", [])) for item in workspace)
    obligation_count = sum(len(item.get("extracted_fields", {}).get("key_obligations", [])) for item in workspace)
    date_count = sum(len(item.get("extracted_fields", {}).get("dates", [])) for item in workspace)
    type_count = len({item.get("extracted_fields", {}).get("document_type", "Unknown") for item in workspace})

    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-top">
                <div>
                    <div class="brand">Legal Doc AI Pipeline</div>
                    <div class="subtle">
                        Open-source, local-first document intelligence for legal workflows, extraction, and grounded Q&A.
                    </div>
                    <div class="badge-row">
                        <span class="badge">Open Source</span>
                        <span class="badge">Local First</span>
                        <span class="badge">Multi-Document Workspace</span>
                        <span class="badge">Cited Answers</span>
                    </div>
                </div>
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Documents</div>
                    <div class="stat-value">{doc_count}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Document Types</div>
                    <div class="stat-value">{type_count}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Dates Found</div>
                    <div class="stat-value">{date_count}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Evidence Chunks</div>
                    <div class="stat-value">{chunk_count}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="Legal Doc AI Pipeline",
    page_icon=":page_facing_up:",
    layout="wide",
)

inject_styles()

if "workspace" not in st.session_state:
    st.session_state.workspace = []
if "query_result" not in st.session_state:
    st.session_state.query_result = None
if "selected_document_id" not in st.session_state:
    st.session_state.selected_document_id = None

try:
    st.session_state.workspace = fetch_workspace()
except Exception:
    pass

if st.session_state.workspace and st.session_state.selected_document_id is None:
    st.session_state.selected_document_id = st.session_state.workspace[0]["document_id"]

render_hero(st.session_state.workspace)

left, center, right = st.columns([1.05, 1.65, 1.25])

with left:
    st.markdown('<div class="section-title">Workspace</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Upload multiple PDFs or images, then review extracted structure per document.</div>',
        unsafe_allow_html=True,
    )
    uploaded_files = st.file_uploader(
        "Upload Documents",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if st.button("Process Documents", type="primary", use_container_width=True):
        if uploaded_files:
            st.session_state.workspace = upload_files(uploaded_files)
            if st.session_state.workspace:
                st.session_state.selected_document_id = st.session_state.workspace[0]["document_id"]
        else:
            st.warning("Upload at least one file.")

    workspace = st.session_state.workspace or fetch_workspace()
    st.session_state.workspace = workspace
    st.markdown(
        f'<div class="toolbar"><div class="toolbar-note">{len(workspace)} document(s) in the current workspace</div></div>',
        unsafe_allow_html=True,
    )
    if workspace:
        st.markdown('<div class="workspace-stack">', unsafe_allow_html=True)
        for index, item in enumerate(workspace):
            is_active = item["document_id"] == st.session_state.selected_document_id
            classes = "mini-card active" if is_active else "mini-card"
            fields = item["extracted_fields"]
            st.markdown(
                f"""
                <div class="{classes}">
                    <div class="file-title">{item['filename']}</div>
                    <div class="file-meta">{fields["document_type"]} · {len(item.get("chunks", []))} chunks</div>
                    <div class="status-row">
                        <span class="status-pill">Parsed</span>
                        <span class="status-pill">{len(fields["dates"])} dates</span>
                        <span class="status-pill">{len(fields["key_obligations"])} obligations</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            button_label = "Selected" if is_active else "Open"
            if st.button(button_label, key=f"doc-select-{item['document_id']}", use_container_width=True):
                st.session_state.selected_document_id = item["document_id"]
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No documents uploaded yet.")

with center:
    st.markdown('<div class="section-title">Extraction</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Structured fields, obligations, and compact summaries generated per document.</div>',
        unsafe_allow_html=True,
    )
    workspace = st.session_state.workspace
    if workspace:
        selected = next(
            (item for item in workspace if item["document_id"] == st.session_state.selected_document_id),
            workspace[0],
        )
        fields = selected["extracted_fields"]
        st.markdown(
            f"""
            <div class="extract-card">
                <div class="extract-heading">{selected['filename']}</div>
                <div class="extract-type">{fields["document_type"] or "Unknown"}</div>
            """,
            unsafe_allow_html=True,
        )
        metric_cols = st.columns(3)
        metric_cols[0].metric("Parties", len(fields["parties"]))
        metric_cols[1].metric("Dates", len(fields["dates"]))
        metric_cols[2].metric("Obligations", len(fields["key_obligations"]))

        st.write("**Summary**")
        st.write(fields["summary"] or "No summary yet.")

        st.write("**Parties**")
        if fields["parties"]:
            st.markdown(
                "".join(f'<span class="chip">{party}</span>' for party in fields["parties"]),
                unsafe_allow_html=True,
            )
        else:
            st.write("No parties extracted")

        st.write("**Dates**")
        if fields["dates"]:
            st.markdown(
                "".join(f'<span class="chip">{date}</span>' for date in fields["dates"]),
                unsafe_allow_html=True,
            )
        else:
            st.write("No dates extracted")

        st.write("**Key Obligations**")
        if fields["key_obligations"]:
            for obligation in fields["key_obligations"]:
                st.markdown(f"- {obligation}")
        else:
            st.write("No obligations extracted")

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Document parsing, OCR fallback, and field extraction will appear here.")

with right:
    st.markdown('<div class="section-title">Ask</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="section-copy">Ask questions across {len(st.session_state.workspace)} document(s) and inspect grounded excerpts returned by the retrieval layer.</div>',
        unsafe_allow_html=True,
    )
    question = st.text_area("Question", placeholder="Ask about dates, parties, clauses, or obligations.")
    if st.button("Run Q&A", type="primary", use_container_width=True):
        st.session_state.query_result = run_query(question)

    result = st.session_state.query_result
    if result:
        st.markdown('<div class="answer-card">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="answer-meta">
                <div class="answer-kicker">Grounded Answer</div>
                <div class="citation-meta">Workspace retrieval response</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("**Answer**")
        st.write(result["answer"])
        st.write("**Citations**")
        if result["citations"]:
            for citation in result["citations"]:
                confidence = citation.get("confidence")
                confidence_text = f"{int(confidence * 100)}% match" if confidence else "Source excerpt"
                page_text = f"Page {citation['page']}" if citation.get("page") else "Page reference pending"
                st.markdown(
                    f"""
                    <div class="citation-card">
                        <div class="citation-top">
                            <div>
                                <div class="file-title">{citation["filename"]}</div>
                                <div class="citation-meta">{page_text}</div>
                            </div>
                            <div class="confidence-pill">{confidence_text}</div>
                        </div>
                        <div style="margin-top: 0.45rem; color: #223229; line-height: 1.5;">{citation["excerpt"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No citations returned yet.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Cited answers with page references will appear here.")
