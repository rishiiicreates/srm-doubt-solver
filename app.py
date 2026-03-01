"""
Streamlit Chat UI — SRM College Doubt-Solving Agent.

Clean, minimal design inspired by portfolio-style navigation.
  - Warm gradient with floating particles
  - Bold, uppercase sidebar navigation
  - @rishiicreates footer
  - Glassmorphic source cards
"""

import streamlit as st

from config import REFUSAL_MESSAGE
from llm import generate_response_stream
from generate_syllabus_kb import SYLLABUS_KB


# ── Page Configuration ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SRM Doubt Solver",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
        --orange: #FF4D00;
        --orange-light: rgba(255, 77, 0, 0.08);
        --deep-black: #131313;
        --charcoal: #2D2D2D;
        --warm-gray: #6B6B6B;
        --light-gray: #9CA3AF;
        --off-white: #FAFAFA;
        --card-bg: rgba(255, 255, 255, 0.65);
        --glass-border: rgba(255, 255, 255, 0.45);
    }

    /* ─── Background ─── */
    .stApp {
        background: linear-gradient(180deg,
            #FFF3E6 0%, #FFDCC8 12%, #F5E6F0 35%,
            #E8EDF8 55%, #F0F4FF 75%, #FAFBFF 100%
        ) !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* ─── Animations ─── */
    @keyframes float-particle {
        0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.35; }
        50% { transform: translateY(-25px) rotate(180deg); opacity: 0.6; }
    }
    @keyframes fade-up {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.4; }
    }

    /* ─── Particles ─── */
    .particles { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; overflow: hidden; }
    .p { position: absolute; border-radius: 50%; animation: float-particle 8s ease-in-out infinite; }
    .p:nth-child(1) { width: 10px; height: 10px; background: rgba(255,77,0,0.15); top: 12%; left: 8%; animation-duration: 7s; }
    .p:nth-child(2) { width: 7px; height: 7px; background: rgba(79,70,229,0.12); top: 28%; right: 12%; animation-delay: 1.5s; animation-duration: 9s; }
    .p:nth-child(3) { width: 13px; height: 13px; background: rgba(232,93,117,0.08); top: 50%; left: 4%; animation-delay: 3s; animation-duration: 11s; }
    .p:nth-child(4) { width: 5px; height: 5px; background: rgba(255,171,118,0.2); top: 65%; right: 6%; animation-delay: 2s; animation-duration: 6s; }
    .p:nth-child(5) { width: 9px; height: 9px; background: rgba(255,77,0,0.1); top: 38%; right: 22%; animation-delay: 4s; animation-duration: 10s; }

    /* ═══════════════════════════════════════════════
       SIDEBAR — Bold, Minimal, Portfolio-Style
       ═══════════════════════════════════════════════ */

    section[data-testid="stSidebar"] {
        background: var(--orange) !important;
        border: none !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
        border-color: rgba(255,255,255,0.15) !important;
    }

    /* ─ Sidebar Brand ─ */
    .sb-brand {
        padding: 1.5rem 0 0.5rem;
        text-align: left;
    }
    .sb-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin: 0;
    }
    .sb-sub {
        font-family: 'Inter', sans-serif;
        font-size: 0.65rem;
        color: rgba(255,255,255,0.65);
        text-transform: uppercase;
        letter-spacing: 3px;
        margin-top: 0.2rem;
    }

    /* ─ Sidebar Divider ─ */
    .sb-div {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.2);
        margin: 1rem 0;
    }

    /* ─ Sidebar Labels ─ */
    section[data-testid="stSidebar"] .stSelectbox label {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        color: rgba(255,255,255,0.8) !important;
    }

    /* ─ Sidebar Selects ─ */
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,0.12) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.85rem !important;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
        background: rgba(255,255,255,0.2) !important;
        border-color: rgba(255,255,255,0.4) !important;
    }
    section[data-testid="stSidebar"] [data-baseweb="select"] span {
        color: white !important;
    }

    /* ─ Sidebar Status ─ */
    .sb-status {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 50px;
        padding: 0.3rem 0.8rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        color: white;
    }
    .sb-dot {
        width: 6px; height: 6px;
        background: #4ade80;
        border-radius: 50%;
        display: inline-block;
        animation: pulse-dot 2s ease-in-out infinite;
    }

    /* ─ Sidebar Info ─ */
    .sb-info {
        font-family: 'Inter', sans-serif;
        font-size: 0.68rem;
        color: rgba(255,255,255,0.55);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: -0.2rem;
    }

    /* ─ Sidebar Button ─ */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.15) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        border-radius: 8px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        padding: 0.45rem 1rem !important;
        transition: all 0.25s ease !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.25) !important;
        border-color: rgba(255,255,255,0.45) !important;
        transform: translateY(-1px) !important;
    }

    /* ─ Sidebar Footer ─ */
    .sb-footer {
        font-family: 'Space Grotesk', sans-serif;
        color: rgba(255,255,255,0.5);
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-align: center;
        padding: 0.5rem 0;
    }
    .sb-footer a {
        color: white !important;
        text-decoration: none;
        font-weight: 700;
        letter-spacing: 1.5px;
    }

    /* ═══════════════════════════════════════════════
       HERO HEADER
       ═══════════════════════════════════════════════ */
    .hero {
        text-align: center;
        padding: 2rem 1rem 1rem;
        animation: fade-up 0.7s ease-out;
    }
    .hero-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 3rem;
        font-weight: 700;
        color: var(--deep-black);
        line-height: 1.15;
        margin: 0 0 0.6rem 0;
        letter-spacing: -0.5px;
    }
    .hero-title .hl {
        background: linear-gradient(135deg, var(--orange), #E85D75);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-sub {
        font-family: 'Inter', sans-serif;
        color: var(--warm-gray);
        font-size: 0.95rem;
        line-height: 1.55;
        max-width: 440px;
        margin: 0 auto;
    }

    /* ═══════════════════════════════════════════════
       CHAT & MESSAGES
       ═══════════════════════════════════════════════ */
    .stChatMessage {
        border-radius: 14px !important;
        margin-bottom: 0.6rem;
        animation: fade-up 0.35s ease-out;
    }
    [data-testid="stChatMessageContent"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem;
        line-height: 1.7;
        color: var(--charcoal);
    }

    /* Chat input */
    .stChatInput > div {
        border-radius: 50px !important;
        border: 2px solid rgba(255,77,0,0.12) !important;
        background: rgba(255,255,255,0.85) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04) !important;
        transition: all 0.3s ease !important;
    }
    .stChatInput > div:focus-within {
        border-color: var(--orange) !important;
        box-shadow: 0 4px 20px rgba(255,77,0,0.1) !important;
    }
    .stChatInput button {
        background: var(--deep-black) !important;
        border-radius: 50px !important;
        color: white !important;
        border: none !important;
        transition: all 0.25s ease !important;
    }
    .stChatInput button:hover {
        background: var(--charcoal) !important;
        transform: scale(1.05);
    }

    /* ═══════════════════════════════════════════════
       SOURCE CARDS
       ═══════════════════════════════════════════════ */
    .src-card {
        background: var(--card-bg);
        backdrop-filter: blur(14px);
        border: 1px solid var(--glass-border);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        margin-top: 0.8rem;
        box-shadow: 0 3px 16px rgba(0,0,0,0.05);
        animation: fade-up 0.4s ease-out;
    }
    .src-card h4 {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--orange);
        margin: 0 0 0.6rem 0;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .src-item {
        background: rgba(255,255,255,0.45);
        border-left: 3px solid var(--orange);
        padding: 0.5rem 0.8rem;
        margin-bottom: 0.4rem;
        border-radius: 0 8px 8px 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.78rem;
        color: var(--charcoal);
        transition: all 0.2s ease;
    }
    .src-item:hover {
        background: var(--orange-light);
        transform: translateX(3px);
    }
    .src-item strong { color: var(--orange); font-weight: 600; }

    /* ─── Hide defaults ─── */
    .stDeployButton, #MainMenu, footer, header { display: none !important; visibility: hidden !important; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,77,0,0.15); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Particles ─────────────────────────────────────────────────────────────────
st.markdown('<div class="particles"><div class="p"></div><div class="p"></div><div class="p"></div><div class="p"></div><div class="p"></div></div>', unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_syllabus_semesters() -> list[int]:
    return sorted(set(info["semester"] for info in SYLLABUS_KB.values()))

def get_subjects_for_semester(semester: int) -> list[str]:
    return sorted(name for name, info in SYLLABUS_KB.items() if info["semester"] == semester)

def get_all_subjects() -> list[str]:
    return sorted(SYLLABUS_KB.keys())

def format_sources_html(sources: list[dict]) -> str:
    if not sources:
        return ""
    seen = set()
    html = '<div class="src-card"><h4>Referenced Topics</h4>'
    for src in sources:
        key = (src.get("subject", ""), src.get("semester", ""), src.get("unit_name", src.get("unit_number", "")))
        if key in seen:
            continue
        seen.add(key)
        parts = []
        if src.get("subject"):
            parts.append(f"<strong>{src['subject']}</strong>")
        if src.get("semester"):
            parts.append(f"Sem {src['semester']}")
        unit_name = src.get("unit_name", "")
        if unit_name:
            parts.append(f"{unit_name}")
        elif src.get("unit_number"):
            parts.append(f"Unit {src['unit_number']}")
        html += f'<div class="src-item">{" · ".join(parts)}</div>'
    html += "</div>"
    return html


# ── Session State ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources_map" not in st.session_state:
    st.session_state.sources_map = {}


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        '<div class="sb-brand">'
        '<p class="sb-name">SRM Doubt<br>Solver.</p>'
        '<p class="sb-sub">AI Study Companion</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="sb-div">', unsafe_allow_html=True)

    # Semester
    semesters = get_syllabus_semesters()
    sem_options = ["All Semesters"] + [f"Semester {s}" for s in semesters]
    selected_sem = st.selectbox("Semester", options=sem_options, index=0)
    selected_sem_num = int(selected_sem.split()[-1]) if selected_sem != "All Semesters" else None

    # Subject
    subjects = get_subjects_for_semester(selected_sem_num) if selected_sem_num else get_all_subjects()
    subj_options = ["All Subjects"] + subjects
    selected_subject = st.selectbox("Subject", options=subj_options, index=0)

    count_text = f"{len(subjects)} subjects in Sem {selected_sem_num}" if selected_sem_num else f"{len(SYLLABUS_KB)} subjects · {len(semesters)} semesters"
    st.markdown(f'<p class="sb-info">{count_text}</p>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-div">', unsafe_allow_html=True)

    # Status
    from retriever import get_retriever
    try:
        doc_count = get_retriever().collection_count
        if doc_count > 0:
            st.markdown(f'<span class="sb-status"><span class="sb-dot"></span> {doc_count} indexed</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="sb-status">⚠ Run ingest.py</span>', unsafe_allow_html=True)
    except Exception:
        st.markdown('<span class="sb-status">⚠ Not ready</span>', unsafe_allow_html=True)

    st.markdown('<hr class="sb-div">', unsafe_allow_html=True)

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sources_map = {}
        st.rerun()

    st.markdown('<hr class="sb-div">', unsafe_allow_html=True)
    st.markdown(
        '<p class="sb-footer"><a href="https://github.com/rishiiicreates" target="_blank">@rishiicreates</a></p>',
        unsafe_allow_html=True,
    )


# ── Hero ──────────────────────────────────────────────────────────────────────

st.markdown(
    '<div class="hero">'
    '<h1 class="hero-title">Ask your <span class="hl">doubts</span>,<br>get expert answers</h1>'
    '<p class="hero-sub">Covers every subject in the SRM syllabus. Detailed, professor-quality explanations.</p>'
    '</div>',
    unsafe_allow_html=True,
)


# ── Chat History ──────────────────────────────────────────────────────────────

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and i in st.session_state.sources_map:
            srcs = st.session_state.sources_map[i]
            if srcs:
                st.markdown(format_sources_html(srcs), unsafe_allow_html=True)


# ── Chat Input ────────────────────────────────────────────────────────────────

if prompt := st.chat_input("What would you like to understand?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        semester_filter = selected_sem_num
        subject_filter = selected_subject if selected_subject != "All Subjects" else None

        with st.spinner("Thinking..."):
            resp_ph = st.empty()
            src_ph = st.empty()
            full_response = ""
            final_sources = []

            for chunk in generate_response_stream(prompt, semester_filter, subject_filter):
                if chunk["type"] == "refusal":
                    full_response = chunk["content"]
                    resp_ph.markdown(full_response)
                    break
                elif chunk["type"] == "sources":
                    final_sources = chunk["sources"]
                elif chunk["type"] == "token":
                    full_response += chunk["content"]
                    resp_ph.markdown(full_response + "●")
                elif chunk["type"] == "done":
                    full_response = chunk["content"]
                    final_sources = chunk.get("sources", final_sources)
                    break

            resp_ph.markdown(full_response)
            if final_sources:
                src_ph.markdown(format_sources_html(final_sources), unsafe_allow_html=True)

    idx = len(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    if final_sources:
        st.session_state.sources_map[idx] = final_sources
