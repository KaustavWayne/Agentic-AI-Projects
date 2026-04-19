"""
QuizForge — AI MCQ Generator
Supports: text notes input + PDF upload
"""
import os
import sys
import logging

# ── CRITICAL: Load .env before ANY other import reads env vars ────────────────
# This must happen before importing services/llm_client etc.
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _project_root)

try:
    from dotenv import load_dotenv
    # override=True so .env always wins even if var was set elsewhere
    load_dotenv(os.path.join(_project_root, ".env"), override=True)
except ImportError:
    pass  # python-dotenv not installed — user must set env vars manually

import streamlit as st
from services.mcq_service import generate_mcqs, MCQGenerationError
from services.pdf_service import extract_text_from_pdf, get_pdf_metadata

logging.basicConfig(level=logging.INFO)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QuizForge · AI MCQ Generator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [data-testid="stAppViewContainer"] {
    background: #F7F4EF !important;
    font-family: 'DM Sans', sans-serif;
    color: #1A1A1A;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
footer { visibility: hidden; }

.qf-header { text-align: center; padding: 3rem 1rem 1.5rem; }
.qf-header h1 {
    font-family: 'DM Serif Display', serif;
    font-size: clamp(2.4rem, 5vw, 4rem);
    font-weight: 400; letter-spacing: -0.02em;
    color: #0D0D0D; margin: 0 0 0.4rem; line-height: 1.1;
}
.qf-header h1 span { color: #D4590A; font-style: italic; }
.qf-header p { font-size: 1.05rem; color: #5C5C5C; font-weight: 300; max-width: 560px; margin: 0 auto; }

.qf-input-card {
    background: #FFFFFF; border: 1.5px solid #E8E3DC;
    border-radius: 20px; padding: 2rem;
    margin: 0 auto 2.5rem; max-width: 780px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.04);
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: #F0EBE3 !important; border-radius: 10px !important;
    padding: 4px !important; gap: 4px !important;
    border: none !important; margin-bottom: 1.2rem;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    border-radius: 8px !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important; font-weight: 500 !important;
    color: #6A6A6A !important; padding: 0.45rem 1.4rem !important;
    background: transparent !important; border: none !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: #FFFFFF !important; color: #0D0D0D !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }

[data-testid="stTextArea"] textarea {
    background: #FAFAF8 !important; border: 1.5px solid #DDD8D0 !important;
    border-radius: 12px !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important; color: #2A2A2A !important;
    padding: 0.9rem 1rem !important; min-height: 180px; resize: vertical;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #D4590A !important;
    box-shadow: 0 0 0 3px rgba(212,89,10,0.08) !important;
}

[data-testid="stFileUploader"] {
    background: #FAFAF8 !important; border: 1.5px dashed #C8C3BC !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] section { padding: 1.5rem !important; }

.qf-pdf-info {
    display: flex; align-items: center; gap: 0.6rem;
    background: #F0EBE3; border: 1px solid #DDD8D0;
    border-radius: 10px; padding: 0.6rem 1rem;
    font-size: 0.85rem; color: #5A4A3A; margin-top: 0.8rem;
}
.qf-pdf-meta { font-weight: 600; color: #0D0D0D; }

.qf-truncation-warn {
    background: #FFF8E1; border: 1px solid #FFD54F;
    border-radius: 8px; padding: 0.6rem 1rem;
    font-size: 0.83rem; color: #7A5F00; margin-top: 0.6rem;
}

[data-testid="stSlider"] > div > div > div > div { background: #D4590A !important; }

[data-testid="stButton"] > button {
    background: #0D0D0D !important; color: #F7F4EF !important;
    border: none !important; border-radius: 12px !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 1rem !important;
    font-weight: 600 !important; padding: 0.75rem 2.5rem !important;
    width: 100%; box-shadow: 0 2px 12px rgba(0,0,0,0.12) !important;
    transition: background 0.2s, transform 0.15s !important;
}
[data-testid="stButton"] > button:hover {
    background: #D4590A !important; transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(212,89,10,0.25) !important;
}

.qf-stats {
    display: flex; gap: 1rem; justify-content: center;
    margin: 0 auto 2rem; max-width: 780px; flex-wrap: wrap;
}
.qf-stat-pill {
    background: #FFFFFF; border: 1.5px solid #E8E3DC;
    border-radius: 100px; padding: 0.45rem 1.2rem;
    font-size: 0.85rem; font-weight: 500; color: #3A3A3A;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.qf-stat-pill span { color: #D4590A; font-weight: 700; }

.qf-grid {
    display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 1.4rem; max-width: 1200px; margin: 0 auto 3rem; padding: 0 1rem;
}
.qf-card {
    background: #FFFFFF; border: 1.5px solid #E8E3DC;
    border-radius: 18px; padding: 1.6rem;
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
    position: relative; overflow: hidden;
}
.qf-card:hover {
    transform: translateY(-3px); box-shadow: 0 12px 36px rgba(0,0,0,0.08);
    border-color: #D4590A;
}
.qf-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #D4590A, #F0A07A); opacity: 0; transition: opacity 0.2s;
}
.qf-card:hover::before { opacity: 1; }

.qf-card-meta { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.qf-badge {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.05em;
    text-transform: uppercase; padding: 0.25rem 0.7rem; border-radius: 100px;
}
.badge-type   { background: #F0EBE3; color: #7A5C3A; }
.badge-easy   { background: #E8F5E8; color: #2D7A2D; }
.badge-medium { background: #FFF3E0; color: #C67A00; }
.badge-hard   { background: #FFEBEE; color: #C62828; }
.badge-num    { background: #0D0D0D; color: #F7F4EF; font-size: 0.72rem; font-weight: 700; padding: 0.25rem 0.7rem; border-radius: 100px; }

.qf-question {
    font-family: 'DM Serif Display', serif; font-size: 1.05rem;
    line-height: 1.55; color: #0D0D0D; margin-bottom: 1.2rem; font-style: italic;
}
.qf-options { display: flex; flex-direction: column; gap: 0.55rem; }
.qf-option {
    display: flex; align-items: flex-start; gap: 0.7rem;
    padding: 0.6rem 0.9rem; border-radius: 10px;
    border: 1.5px solid #EDE9E2; background: #FAFAF8;
    font-size: 0.9rem; line-height: 1.45; transition: all 0.15s;
}
.qf-option:hover { background: #F5F0E8; border-color: #C8BFB0; }
.qf-option.correct { background: #F0FAF0; border-color: #5CB85C; }
.qf-option.correct .opt-label { background: #5CB85C; color: white; }
.opt-label {
    font-weight: 700; font-size: 0.8rem; background: #E8E3DC; color: #5A5A5A;
    width: 24px; height: 24px; min-width: 24px; border-radius: 6px;
    display: flex; align-items: center; justify-content: center; margin-top: 1px;
}

[data-testid="stExpander"] {
    background: #FAFAF8 !important; border: 1px dashed #D8D3CC !important;
    border-radius: 10px !important; margin-top: 1rem !important;
}
[data-testid="stExpander"] summary { font-size: 0.85rem !important; font-weight: 600 !important; color: #7A6A5A !important; }
.qf-explanation { font-size: 0.88rem; color: #4A4A4A; line-height: 1.6; padding: 0.3rem 0.2rem; }

.qf-topic { text-align: center; margin: 0 auto 1.5rem; max-width: 780px; }
.qf-topic-inner {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: #0D0D0D; color: #F7F4EF;
    font-size: 0.85rem; font-weight: 500;
    padding: 0.5rem 1.4rem; border-radius: 100px; letter-spacing: 0.01em;
}
.qf-source-badge {
    background: rgba(255,255,255,0.15); border-radius: 100px;
    padding: 0.2rem 0.7rem; font-size: 0.75rem; font-weight: 600;
}
.qf-error {
    background: #FFF5F5; border: 1.5px solid #FFCDD2; border-radius: 12px;
    padding: 1.2rem 1.5rem; max-width: 780px; margin: 0 auto;
    color: #C62828; font-size: 0.88rem; line-height: 1.6;
}
.qf-empty { text-align: center; padding: 4rem 2rem; color: #9A9A9A; }
.qf-empty-icon { font-size: 3.5rem; margin-bottom: 1rem; }
.qf-empty p { font-size: 1rem; max-width: 400px; margin: 0 auto; }

/* API key banner */
.qf-api-banner {
    background: #FFF8E1; border: 1.5px solid #FFD54F; border-radius: 14px;
    padding: 1.2rem 1.5rem; max-width: 780px; margin: 0 auto 1.5rem;
    color: #5C4A00; font-size: 0.9rem; line-height: 1.7;
}
.qf-api-banner code {
    background: #FFF0B3; padding: 0.15rem 0.45rem;
    border-radius: 5px; font-size: 0.85rem; color: #3A3000;
}

hr { border-color: #E8E3DC !important; margin: 2rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="qf-header">
    <h1>Quiz<span>Forge</span></h1>
    <p>Paste your notes or upload a PDF — get razor-sharp MCQs that test deep understanding, not surface recall.</p>
</div>
""", unsafe_allow_html=True)


# ── API Key Check (show helpful banner instead of bare error) ─────────────────
api_key_set = bool(os.environ.get("GROQ_API_KEY", "").strip())
if not api_key_set:
    st.markdown("""
    <div class="qf-api-banner">
        <strong>⚠️ GROQ_API_KEY not detected.</strong><br>
        Create a file called <code>.env</code> in the project root folder with:<br><br>
        <code>GROQ_API_KEY=gsk_your_key_here</code><br><br>
        Get a free key at <strong>console.groq.com</strong>, then restart the app with:<br>
        <code>uv run streamlit run app/streamlit_app.py</code>
    </div>
    """, unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("mcq_set", None), ("error_msg", None),
    ("source_label", "text"), ("extracted_text", None),
    ("pdf_meta", None), ("was_truncated", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Input Card ────────────────────────────────────────────────────────────────
st.markdown('<div class="qf-input-card">', unsafe_allow_html=True)

tab_text, tab_pdf = st.tabs(["📝  Paste Notes", "📄  Upload PDF"])

notes_from_text = ""

with tab_text:
    notes_from_text = st.text_area(
        label="notes",
        placeholder=(
            "Paste lecture notes, textbook paragraphs, documentation...\n\n"
            "Tip: Richer notes → sharper, more conceptual questions."
        ),
        height=200,
        label_visibility="collapsed",
        key="notes_input",
    )

with tab_pdf:
    uploaded_file = st.file_uploader(
        label="Upload a PDF",
        type=["pdf"],
        help="Recommended: up to ~50 pages. Scanned/image-only PDFs are not supported.",
        label_visibility="collapsed",
        key="pdf_uploader",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        with st.spinner("Extracting text from PDF..."):
            try:
                extracted = extract_text_from_pdf(file_bytes)
                meta = get_pdf_metadata(file_bytes)
                st.session_state.extracted_text = extracted
                st.session_state.pdf_meta = meta
                st.session_state.was_truncated = "[Note: Content truncated" in extracted

                title_str = f" · {meta['title']}" if meta.get("title") else ""
                st.markdown(
                    f'<div class="qf-pdf-info">'
                    f'📄 <span><span class="qf-pdf-meta">{uploaded_file.name}</span>'
                    f'{title_str} · {meta["pages"]} page(s) · '
                    f'{len(extracted):,} chars extracted</span></div>',
                    unsafe_allow_html=True,
                )
                if st.session_state.was_truncated:
                    st.markdown(
                        '<div class="qf-truncation-warn">⚠️ PDF is large — content trimmed to ~12,000 chars. '
                        'MCQs will cover the first portion of the document.</div>',
                        unsafe_allow_html=True,
                    )
            except ValueError as e:
                st.markdown(f'<div class="qf-error">⚠️ {e}</div>', unsafe_allow_html=True)
                st.session_state.extracted_text = None
    else:
        st.session_state.extracted_text = None
        st.session_state.pdf_meta = None

col1, col2 = st.columns([3, 2])
with col1:
    num_questions = st.slider("Number of questions", 3, 15, 5)
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("⚡ Generate MCQs", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)


# ── Generation ────────────────────────────────────────────────────────────────
if generate_btn:
    if st.session_state.extracted_text:
        final_notes  = st.session_state.extracted_text
        source_label = "pdf"
    elif notes_from_text.strip():
        final_notes  = notes_from_text.strip()
        source_label = "text"
    else:
        final_notes  = ""
        source_label = "none"

    if not api_key_set:
        st.session_state.error_msg = (
            "GROQ_API_KEY is not set. Create a .env file in the project root with: "
            "GROQ_API_KEY=gsk_your_key — then restart the app."
        )
        st.session_state.mcq_set = None
    elif source_label == "none":
        st.session_state.error_msg = "Please paste some notes or upload a PDF before generating."
        st.session_state.mcq_set = None
    elif len(final_notes) < 50:
        st.session_state.error_msg = "Content too short. Please provide at least 50 characters."
        st.session_state.mcq_set = None
    else:
        with st.spinner("Forging your questions… this takes ~15–30 seconds"):
            try:
                mcq_set = generate_mcqs(notes=final_notes, num_questions=num_questions)
                st.session_state.mcq_set      = mcq_set
                st.session_state.source_label = source_label
                st.session_state.error_msg    = None
            except (MCQGenerationError, ValueError) as e:
                st.session_state.error_msg = str(e)
                st.session_state.mcq_set   = None
            except Exception as e:
                st.session_state.error_msg = f"Unexpected error: {e}"
                st.session_state.mcq_set   = None


# ── Error ─────────────────────────────────────────────────────────────────────
if st.session_state.error_msg:
    st.markdown(
        f'<div class="qf-error">⚠️ {st.session_state.error_msg}</div>',
        unsafe_allow_html=True,
    )


# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.mcq_set:
    mcq_set = st.session_state.mcq_set
    src = st.session_state.get("source_label", "text")
    src_badge = (
        '<span class="qf-source-badge">📄 PDF</span>'
        if src == "pdf"
        else '<span class="qf-source-badge">📝 Notes</span>'
    )

    st.markdown(
        f'<div class="qf-topic"><div class="qf-topic-inner">'
        f'📚 {mcq_set.topic_summary} {src_badge}</div></div>',
        unsafe_allow_html=True,
    )

    types        = [q.question_type for q in mcq_set.questions]
    difficulties = [q.difficulty     for q in mcq_set.questions]
    st.markdown(f"""
    <div class="qf-stats">
        <div class="qf-stat-pill">⚡ <span>{mcq_set.total_questions}</span> Questions</div>
        <div class="qf-stat-pill">🧠 <span>{types.count('conceptual')}</span> Conceptual</div>
        <div class="qf-stat-pill">🔬 <span>{types.count('application')}</span> Application</div>
        <div class="qf-stat-pill">🔍 <span>{types.count('inference')}</span> Inference</div>
        <div class="qf-stat-pill">🔥 <span>{difficulties.count('hard')}</span> Hard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="qf-grid">', unsafe_allow_html=True)
    for i, mcq in enumerate(mcq_set.questions):
        options_html = "".join(
            f'<div class="qf-option{"  correct" if o.label == mcq.correct_answer else ""}">'
            f'<span class="opt-label">{o.label}</span><span>{o.text}</span></div>'
            for o in mcq.options
        )
        st.markdown(f"""
        <div class="qf-card">
            <div class="qf-card-meta">
                <span class="qf-badge badge-num">Q{i+1}</span>
                <span class="qf-badge badge-type">{mcq.question_type.capitalize()}</span>
                <span class="qf-badge badge-{mcq.difficulty}">{mcq.difficulty.capitalize()}</span>
            </div>
            <div class="qf-question">{mcq.question}</div>
            <div class="qf-options">{options_html}</div>
        </div>
        """, unsafe_allow_html=True)
        with st.expander(f"💡 Explanation — Q{i+1}"):
            st.markdown(
                f'<div class="qf-explanation">{mcq.explanation}</div>',
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center;color:#9A9A9A;font-size:0.8rem;'>"
        "© Kaustav Roy Chowdhury · QuizForge · Powered by Groq + LangGraph</p>",
        unsafe_allow_html=True,
    )

elif not st.session_state.error_msg:
    st.markdown("""
    <div class="qf-empty">
        <div class="qf-empty-icon">✦</div>
        <p>Paste notes or upload a PDF, then hit <strong>Generate MCQs</strong>.</p>
    </div>
    """, unsafe_allow_html=True)
