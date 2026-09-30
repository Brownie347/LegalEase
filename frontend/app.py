"""LegalEase - Streamlit frontend.

Run from the project root:
    streamlit run frontend/app.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import requests  # noqa: E402
import streamlit as st  # noqa: E402

import config  # noqa: E402
from ai_core.generator import (  # noqa: E402
    format_docx,
    format_html_preview,
    format_pdf,
    sanitize_text,
)

# --------------------------------------------------------------------------- #
# Page setup
# --------------------------------------------------------------------------- #
st.set_page_config(page_title="LegalEase", page_icon="⚖️", layout="centered")

st.markdown(
    """
    <style>
      .stButton > button, .stDownloadButton > button { border-radius: 8px; }
      .preview-card {
        background:#0f1524; border:1px solid #263048; border-radius:12px;
        padding:20px 24px; max-height:440px; overflow-y:auto;
        font-family: Georgia, 'Times New Roman', serif; line-height:1.55;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

_, logo_col, _ = st.columns([1, 2, 1])
with logo_col:
    if config.WEB_LOGO_PATH.exists():
        st.image(str(config.WEB_LOGO_PATH), width=280)
    else:
        st.markdown("<h1 style='text-align:center'>⚖️ LegalEase</h1>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>AI Legal Document Generator</h2>", unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
# Session state
# --------------------------------------------------------------------------- #
for key, default in (("generated_text", ""), ("show_edit", False), ("meta", {})):
    st.session_state.setdefault(key, default)


def toggle_edit():
    st.session_state.show_edit = not st.session_state.show_edit


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "document"


def backend_error(exc: Exception) -> str:
    if isinstance(exc, requests.ConnectionError):
        return (
            f"Cannot reach the backend at {config.BACKEND_URL}. "
            "Start it with:  uvicorn legalEaseAPI.main:app --reload"
        )
    if isinstance(exc, requests.Timeout):
        return "The request timed out. The model may be busy - please try again."
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        try:
            detail = exc.response.json().get("detail")
        except ValueError:
            detail = None
        if isinstance(detail, list):  # FastAPI validation errors
            detail = "; ".join(str(d.get("msg", d)) for d in detail)
        return str(detail or f"Backend returned HTTP {exc.response.status_code}.")
    return f"Unexpected error: {exc}"


# --------------------------------------------------------------------------- #
# Input form
# --------------------------------------------------------------------------- #
document_type = st.text_input("Document Type (Ex: Agreement, Contract, NDA)")
parties = st.text_area("Parties Involved")
terms = st.text_area("Terms & Conditions (Use semicolons for bullet points)")
dates = st.text_input("Effective Date")

if st.button("Generate Document"):
    if not document_type.strip() or not parties.strip():
        st.warning("Please fill in at least the Document Type and Parties Involved.")
    else:
        try:
            with st.spinner("Drafting your document with Gemini..."):
                # Send to backend
                response = requests.post(
                    f"{config.BACKEND_URL}/generate",
                    json={
                        "document_type": document_type,
                        "parties": parties,
                        "terms": terms,
                        "dates": dates,
                    },
                    timeout=config.GEMINI_TIMEOUT_SECONDS * (config.GEMINI_MAX_RETRIES + 2),
                )
                response.raise_for_status()
            generated_text = sanitize_text(response.json()["document"])
            st.session_state.generated_text = generated_text
            st.session_state.meta = {
                "document_type": document_type.strip(),
                "parties": parties.strip(),
                "terms": terms.strip(),
                "dates": dates.strip(),
            }
            st.session_state.show_edit = False
            st.session_state.pop("editor_text", None)
            st.success("✅ Document Generated Successfully!")
        except (requests.RequestException, KeyError, ValueError) as exc:
            st.error(f"❌ {backend_error(exc)}")

# --------------------------------------------------------------------------- #
# Preview / edit / download
# --------------------------------------------------------------------------- #
if st.session_state.generated_text:
    # Keep the stored text in sync with the editor (if it is open).
    if st.session_state.show_edit and "editor_text" in st.session_state:
        st.session_state.generated_text = st.session_state.editor_text

    generated_text = st.session_state.generated_text
    meta = st.session_state.meta or {}

    styled_html = format_html_preview(generated_text)
    st.markdown(f"<div class='preview-card'>{styled_html}</div>", unsafe_allow_html=True)

    st.button(
        "✖ Close Editor" if st.session_state.show_edit else "✏️ Click to Edit Document",
        on_click=toggle_edit,
    )

    if st.session_state.show_edit:
        if "editor_text" not in st.session_state:
            st.session_state.editor_text = generated_text
        st.text_area("Edit Document Below:", key="editor_text", height=300)
        st.caption("Press Ctrl+Enter (or click outside the box) to apply your edits.")
        generated_text = st.session_state.editor_text

    doc_type = meta.get("document_type") or "Legal Document"
    base_name = slugify(doc_type)
    fmt_kwargs = dict(
        terms=meta.get("terms", ""),
        parties=meta.get("parties", ""),
        effective_date=meta.get("dates", ""),
    )

    st.download_button(
        "📄 Download as .TXT",
        data=generated_text,
        file_name=f"{base_name}.txt",
        mime="text/plain",
    )
    st.download_button(
        "📝 Download as .DOCX",
        data=format_docx(generated_text, doc_type, **fmt_kwargs),
        file_name=f"{base_name}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    st.download_button(
        "📕 Download as .PDF",
        data=format_pdf(generated_text, doc_type, **fmt_kwargs),
        file_name=f"{base_name}.pdf",
        mime="application/pdf",
    )
    st.caption(
        "⚠️ AI-generated drafts are for general information only and are not legal advice. "
        "Have a qualified lawyer review any document before you sign or rely on it."
    )
else:
    st.info("Click 'Generate Document' to start")
