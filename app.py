"""
Streamlit Chat UI — Doubt-Solving Agent.

Clean, minimal design with right-side floating nav panel.
  - Warm gradient with floating particles
  - Floating ☰ button on the right that opens a panel
  - Inline filters in main area
  - Glassmorphic source cards
  - 'built by rishiicreates and friends' footer
"""

import streamlit as st
import hashlib
from typing import Generator
import time

from config import REFUSAL_MESSAGE, CHROMA_PERSIST_DIR
import os

# --- Auto-Ingestion for Cloud Deployments ---
def check_and_run_ingestion():
    if "ingestion_done" not in st.session_state:
        # Check if chroma db exists and is not empty
        if not os.path.exists(CHROMA_PERSIST_DIR) or not os.listdir(CHROMA_PERSIST_DIR):
            with st.spinner("First-time setup: Downloading and indexing syllabus data (this takes a few minutes)..."):
                try:
                    import ingest
                    ingest.main()
                    st.success("Successfully indexed syllabus data!")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to auto-ingest data: {e}")
        st.session_state.ingestion_done = True

check_and_run_ingestion()
# --------------------------------------------

from llm import generate_response_stream
from retriever import SYLLABUS_KB


# ── Page Configuration ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Doubt Solver",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
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

    /* ─── Completely hide sidebar ─── */
    section[data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
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
    @keyframes slide-in-right {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slide-out-right {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
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

    /* ═══════════════════════════════════════════════
       FOOTER
       ═══════════════════════════════════════════════ */
    .site-footer {
        position: fixed;
        bottom: 8px;
        right: 20px;
        display: flex;
        justify-content: flex-end;
        align-items: center;
        z-index: 100000;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.65rem;
        color: #9CA3AF;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        pointer-events: none;
    }
    .site-footer a {
        color: var(--orange);
        text-decoration: none;
        font-weight: 700;
        pointer-events: auto;
    }
    .site-footer a:hover { opacity: 0.8; }

    [data-testid="stBottomBlockContainer"] {
        padding-bottom: 2rem !important;
    }

    /* ─── Hide defaults & sync inputs ─── */
    .stDeployButton, #MainMenu, footer, header { display: none !important; visibility: hidden !important; }
    div[data-testid="stTextInput"] { display: none !important; }

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


# ── Build filter options for nav panel ────────────────────────────────────────

from retriever import get_retriever
try:
    doc_count = get_retriever().collection_count
    status_text = f"{doc_count} indexed"
except Exception:
    status_text = "Not ready"

total_subjects_count = len(SYLLABUS_KB)
semesters = get_syllabus_semesters()
total_semesters = len(semesters)
all_subjects = get_all_subjects()


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
            parts.append(f"Unit: {unit_name}")
        elif src.get("unit_number"):
            parts.append(f"Unit {src['unit_number']}")
        score = src.get("similarity_score", 0)
        if score:
            pct = int(score * 100)
            parts.append(f'<span style="opacity:0.5;font-size:0.7rem">{pct}% match</span>')
        html += f'<div class="src-item">{" · ".join(parts)}</div>'
    html += "</div>"
    return html


# ── Read filter values — session_state is authoritative, hidden inputs update it ──

# Filters are removed from UI. Defaulting to None for global search.
selected_sem_num = None
selected_subject = None

# Debug: Print active filters to Streamlit server log
print(f"  🔍 Active filters — semester: {selected_sem_num}, subject: {selected_subject}")


# ── Session State ─────────────────────────────────────────────────────────────
# This must remain for initialization if it wasn't already caught above
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources_map" not in st.session_state:
    st.session_state.sources_map = {}


# ── Hero ──────────────────────────────────────────────────────────────────────

st.markdown(
    '<div class="hero">'
    '<h1 class="hero-title">What do you want<br>to <span class="hl">learn</span> today?</h1>'
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
        subject_filter = selected_subject
        print(f"  🚀 Generating response — query='{prompt}', sem={semester_filter}, subj={subject_filter}")

        # Pass the last 5 messages (excluding the current user prompt we just appended)
        # to give the LLM conversational memory.
        chat_context = st.session_state.messages[:-1][-5:]

        with st.spinner("Thinking..."):
            resp_ph = st.empty()
            src_ph = st.empty()
            full_response = ""
            final_sources = []

            for chunk in generate_response_stream(prompt, semester_filter, subject_filter, chat_history=chat_context):
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

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="site-footer">
    <a href="https://my-portfolio-drab-nu-83.vercel.app/" target="_blank">@rishiicreates</a>
</div>
""", unsafe_allow_html=True)
