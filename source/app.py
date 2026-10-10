import streamlit as st
import json
from PIL import Image
from gemini_client import get_model
from prompts import EXTRACTION_PROMPT, QA_PROMPT_PREFIX

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bill Decoder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body {
    font-family: 'Inter', sans-serif;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 3rem 3rem !important; }

/* ── Hero ─────────────────────────────── */
.hero {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.25rem;
}
.hero-icon {
    font-size: 2.4rem;
    line-height: 1;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #0F172A;
    margin: 0;
    letter-spacing: -0.5px;
}
.hero-sub {
    color: #64748B;
    font-size: 0.95rem;
    margin: 0 0 2rem 0;
}

/* ── Upload area ──────────────────────── */
.upload-label {
    font-size: 0.85rem;
    font-weight: 500;
    color: #334155;
    margin-bottom: 0.4rem;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}

/* ── Card ─────────────────────────────── */
.card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.card-title {
    font-size: 0.75rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 0.8rem;
}

/* ── Tab bar ─────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid #E2E8F0;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    padding: 0.6rem 1.4rem;
    font-size: 0.9rem;
    font-weight: 500;
    color: #64748B;
    border: none;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    color: #6366F1 !important;
    border-bottom: 2px solid #6366F1 !important;
    font-weight: 600;
}

/* ── Buttons ─────────────────────────── */
.stButton > button {
    background: #6366F1;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.55rem 1.4rem;
    font-weight: 600;
    font-size: 0.9rem;
    transition: background 0.2s, transform 0.15s;
    width: 100%;
}
.stButton > button:hover {
    background: #4F46E5;
    transform: translateY(-1px);
}

/* ── Divider ─────────────────────────── */
hr { border-color: #F1F5F9; margin: 1.5rem 0; }



/* ── Image container ─────────────────── */
.img-caption {
    font-size: 0.78rem;
    color: #94A3B8;
    margin-top: 0.5rem;
    text-align: center;
}

/* ── Answer box ──────────────────────── */
.answer-box {
    background: #F8FAFC;
    border-left: 3px solid #6366F1;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    color: #1E293B;
    font-size: 0.93rem;
    line-height: 1.7;
}
</style>
""", unsafe_allow_html=True)

# ─── Load model ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return get_model()

try:
    model = load_model()
except Exception as e:
    st.error(f"Could not initialize model: {e}")
    st.stop()

# ─── Helper functions ────────────────────────────────────────────────────────
def run_extraction(image):
    response = model.generate_content([EXTRACTION_PROMPT, image])
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())

def run_qa(image, question):
    response = model.generate_content([QA_PROMPT_PREFIX + question.strip(), image])
    return response.text.strip()

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <span class="hero-icon">⚡</span>
    <h1 class="hero-title">Bill Decoder</h1>
</div>
<p class="hero-sub">Upload a K-Electric, LESCO, or IESCO bill to extract data or get instant answers.</p>
""", unsafe_allow_html=True)

# ─── Upload ───────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Upload bill image (JPG or PNG)",
    type=["jpg", "jpeg", "png"]
)

if not uploaded_file:
    st.markdown("""
    <div class="card" style="text-align:center; padding: 3rem 2rem; color:#94A3B8;">
        <div style="font-size:2.5rem;margin-bottom:0.75rem;">📂</div>
        <div style="font-weight:600;font-size:1rem;color:#475569;margin-bottom:0.4rem;">Drop your bill here</div>
        <div style="font-size:0.85rem;">Supported: JPG, PNG · Up to 5 MB</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── Main layout ─────────────────────────────────────────────────────────────
image = Image.open(uploaded_file)
left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown('<div class="card-title">Bill Preview</div>', unsafe_allow_html=True)
    st.image(image, use_container_width=True)
    size_kb = uploaded_file.size / 1024
    st.markdown(f'<p class="img-caption">{uploaded_file.name} &nbsp;·&nbsp; {size_kb:.0f} KB &nbsp;·&nbsp; {image.width} × {image.height}px</p>', unsafe_allow_html=True)

with right:
    tab1, tab2 = st.tabs(["  📊  Extract Data  ", "  💬  Ask a Question  "])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        extract_btn = st.button("Extract Bill Data", key="extract_btn")
        if extract_btn:
            with st.spinner("Reading bill..."):
                try:
                    result = run_extraction(image)
                    st.success("Extracted successfully")
                    st.json(result)
                except json.JSONDecodeError:
                    st.error("Could not parse the model response as JSON.")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        question = st.text_input(
            "Question",
            placeholder="e.g. What are my total taxes this month?",
            label_visibility="collapsed"
        )
        ask_btn = st.button("Get Answer", key="ask_btn")
        if ask_btn and question:
            with st.spinner("Analyzing..."):
                try:
                    answer = run_qa(image, question)
                    st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")
        elif ask_btn and not question:
            st.warning("Please type a question first.")
