"""
Streamlit Chat UI — SRM College Doubt-Solving Agent.

Sarvam.ai-inspired warm gradient + portfolio-inspired bold sidebar.
Clean, minimal, no extra text. @rishiicreates trademark.
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
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Playfair+Display:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    /* ─── Variables ─── */
    :root {
        --orange-accent: #FF4D00;
        --warm-orange: #FF6B2C;
        --deep-black: #0D0D0D;
        --charcoal: #1A1A1A;
        --off-white: #F5F0EB;
        --warm-cream: #FAF7F2;
        --text-primary: #0D0D0D;
        --text-secondary: #5C5C5C;
        --text-muted: #9A9A9A;
        --glass-bg: rgba(255, 255, 255, 0.65);
        --glass-border: rgba(0, 0, 0, 0.06);
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
        --shadow-md: 0 4px 20px rgba(0,0,0,0.06);
        --shadow-lg: 0 8px 40px rgba(0,0,0,0.08);
    }

    /* ─── Global ─── */
    .stApp {
        background: linear-gradient(170deg,
            #FFF0E0 0%,
            #FFEBD4 10%,
            #FAF0F0 25%,
            #F0EFF8 45%,
            #EDF2FC 65%,
            #F5F7FF 100%
        ) !important;
        font-family: 'Space Grotesk', -apple-system, sans-serif;
    }

    /* ─── Animations ─── */
    @keyframes fade-in {
        from { opacity: 0; transform: translateY(16px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulse-dot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.85); }
    }

    @keyframes float-subtle {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-6px); }
    }

    @keyframes shimmer-line {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    /* ─── Sidebar ─── */
    section[data-testid="stSidebar"] {
        background: var(--deep-black) !important;
        border-right: none !important;
    }

    section[data-testid="stSidebar"] * {
        color: var(--off-white) !important;
    }

    section[data-testid="stSidebar"] .stSelectbox label {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.7rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        color: var(--text-muted) !important;
    }

    /* Sidebar brand */
    .sidebar-brand {
        text-align: left;
        padding: 0.5rem 0 1rem;
    }

    .sidebar-logo {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        color: white !important;
        margin: 0;
        letter-spacing: -1px;
        line-height: 1.1;
        text-transform: uppercase;
    }

    .sidebar-tagline {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--text-muted) !important;
        font-size: 0.65rem;
        margin-top: 0.3rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        font-weight: 500;
    }

    /* Sidebar divider */
    .sidebar-line {
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        margin: 1rem 0;
    }

    /* Status pill in sidebar */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 0.3rem 0.7rem;
        border-radius: 50px;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .status-live {
        background: rgba(34, 197, 94, 0.12);
        color: #4ADE80 !important;
        border: 1px solid rgba(34, 197, 94, 0.15);
    }

    .status-live .dot {
        width: 5px;
        height: 5px;
        background: #4ADE80;
        border-radius: 50%;
        display: inline-block;
        animation: pulse-dot 2s ease-in-out infinite;
    }

    .status-warn {
        background: rgba(245, 158, 11, 0.12);
        color: #FBBF24 !important;
        border: 1px solid rgba(245, 158, 11, 0.15);
    }

    /* Sidebar subject count */
    .meta-text {
        font-family: 'Space Grotesk', sans-serif;
        color: rgba(255,255,255,0.25) !important;
        font-size: 0.65rem;
        margin-top: -4px;
        letter-spacing: 0.5px;
    }

    /* Sidebar footer / trademark */
    .trademark {
        font-family: 'Space Grotesk', sans-serif;
        color: rgba(255, 255, 255, 0.2) !important;
        font-size: 0.65rem;
        text-align: center;
        letter-spacing: 1px;
        padding: 0.5rem 0;
    }

    .trademark a {
        color: var(--orange-accent) !important;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.2s ease;
    }

    .trademark a:hover {
        color: var(--warm-orange) !important;
    }

    /* Selectbox styling inside dark sidebar */
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: white !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
        border-color: var(--orange-accent) !important;
        background: rgba(255, 77, 0, 0.06) !important;
    }

    /* Clear chat button */
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: rgba(255, 255, 255, 0.5) !important;
        border-radius: 10px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.25s ease !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        border-color: var(--orange-accent) !important;
        color: var(--orange-accent) !important;
        background: rgba(255, 77, 0, 0.06) !important;
    }

    /* ─── Hero Header ─── */
    .hero {
        text-align: center;
        padding: 3rem 1rem 2rem;
        animation: fade-in 0.7s ease-out;
    }

    .hero-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 3.5rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.1;
        margin: 0 0 0.6rem 0;
        letter-spacing: -1.5px;
    }

    .hero-title .accent {
        color: var(--orange-accent);
    }

    .hero-sub {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--text-secondary);
        font-size: 1rem;
        font-weight: 400;
        max-width: 420px;
        margin: 0 auto 1.5rem;
        line-height: 1.5;
    }

    .stats-row {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .stat-chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 50px;
        padding: 0.35rem 0.85rem;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        color: var(--text-primary);
        box-shadow: var(--shadow-sm);
        transition: all 0.25s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stat-chip:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }

    /* ─── Chat Messages ─── */
    .stChatMessage {
        border-radius: 14px !important;
        margin-bottom: 0.5rem;
        animation: fade-in 0.35s ease-out;
    }

    [data-testid="stChatMessageContent"] {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.95rem;
        line-height: 1.75;
        color: var(--text-primary);
        font-weight: 400;
    }

    [data-testid="stChatMessageContent"] strong,
    [data-testid="stChatMessageContent"] b {
        font-weight: 700;
    }

    [data-testid="stChatMessageContent"] h1,
    [data-testid="stChatMessageContent"] h2,
    [data-testid="stChatMessageContent"] h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }

    /* ─── Source Cards ─── */
    .src-card {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        margin-top: 0.8rem;
        box-shadow: var(--shadow-sm);
        animation: fade-in 0.45s ease-out;
    }

    .src-card h4 {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--orange-accent);
        margin: 0 0 0.6rem 0;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    .src-item {
        border-left: 3px solid var(--orange-accent);
        padding: 0.45rem 0.8rem;
        margin-bottom: 0.4rem;
        border-radius: 0 8px 8px 0;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 0.78rem;
        color: var(--text-primary);
        font-weight: 500;
        background: rgba(255, 77, 0, 0.03);
        transition: all 0.2s ease;
    }

    .src-item:hover {
        background: rgba(255, 77, 0, 0.06);
        transform: translateX(3px);
    }

    .src-item strong {
        color: var(--orange-accent);
        font-weight: 700;
    }

    /* ─── Chat Input ─── */
    .stChatInput > div {
        border-radius: 50px !important;
        border: 2px solid rgba(0, 0, 0, 0.08) !important;
        background: rgba(255, 255, 255, 0.8) !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.3s ease !important;
        padding: 0.1rem 0.2rem !important;
    }

    .stChatInput > div:focus-within {
        border-color: var(--orange-accent) !important;
        box-shadow: 0 0 0 3px rgba(255, 77, 0, 0.08) !important;
    }

    /* Send button */
    .stChatInput button {
        background: var(--deep-black) !important;
        border-radius: 50px !important;
        color: white !important;
        box-shadow: inset 0 1px 8px rgba(255,255,255,0.08) !important;
        transition: all 0.25s ease !important;
        border: none !important;
    }

    .stChatInput button:hover {
        background: var(--charcoal) !important;
        transform: scale(1.06);
        box-shadow: inset 0 1px 12px rgba(255,255,255,0.12),
                    0 4px 12px rgba(0,0,0,0.12) !important;
    }

    /* ─── Hide Streamlit Chrome ─── */
    .stDeployButton { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ─── Scrollbar ─── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.08);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(0, 0, 0, 0.15); }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────


def get_syllabus_semesters() -> list[int]:
    return sorted(set(info["semester"] for info in SYLLABUS_KB.values()))


def get_subjects_for_semester(semester: int) -> list[str]:
    return sorted(
        name for name, info in SYLLABUS_KB.items()
        if info["semester"] == semester
    )


def get_all_subjects() -> list[str]:
    return sorted(SYLLABUS_KB.keys())


def format_sources_html(sources: list[dict]) -> str:
    if not sources:
        return ""

    seen = set()
    items = []
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
            parts.append(unit_name)
        elif src.get("unit_number"):
            parts.append(f"Unit {src['unit_number']}")

        items.append(f'<div class="src-item">{" &nbsp;·&nbsp; ".join(parts)}</div>')

    if not items:
        return ""

    return (
        '<div class="src-card">'
        '<h4>Referenced Topics</h4>'
        + "".join(items)
        + '</div>'
    )


# ── Session State ────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "sources_map" not in st.session_state:
    st.session_state.sources_map = {}


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">'
        '<p class="sidebar-logo">SRM<br>Doubt<br>Solver</p>'
        '<p class="sidebar-tagline">AI Study Companion</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="sidebar-line">', unsafe_allow_html=True)

    semesters = get_syllabus_semesters()
    semester_options = ["All Semesters"] + [f"Semester {s}" for s in semesters]

    selected_sem_display = st.selectbox(
        "SEMESTER",
        options=semester_options,
        index=0,
    )

    selected_sem = None
    if selected_sem_display != "All Semesters":
        selected_sem = int(selected_sem_display.split()[-1])

    subjects = get_subjects_for_semester(selected_sem) if selected_sem else get_all_subjects()
    subject_options = ["All Subjects"] + subjects

    selected_subject = st.selectbox(
        "SUBJECT",
        options=subject_options,
        index=0,
    )

    if selected_sem:
        st.markdown(f'<p class="meta-text">{len(subjects)} subjects</p>', unsafe_allow_html=True)

    st.markdown('<hr class="sidebar-line">', unsafe_allow_html=True)

    # Status
    from retriever import get_retriever
    try:
        retriever = get_retriever()
        doc_count = retriever.collection_count
        if doc_count > 0:
            st.markdown(
                f'<span class="status-pill status-live">'
                f'<span class="dot"></span>{doc_count} indexed</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="status-pill status-warn">⚠ Run ingest.py</span>',
                unsafe_allow_html=True,
            )
    except Exception:
        st.markdown(
            '<span class="status-pill status-warn">⚠ Not ready</span>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sidebar-line">', unsafe_allow_html=True)

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sources_map = {}
        st.rerun()

    st.markdown('<hr class="sidebar-line">', unsafe_allow_html=True)

    st.markdown(
        '<p class="trademark">'
        'Built by <a href="https://github.com/rishiiicreates" target="_blank">@rishiicreates</a>'
        '</p>',
        unsafe_allow_html=True,
    )


# ── Hero ─────────────────────────────────────────────────────────────────────

topic_count = sum(len(v["units"]) for v in SYLLABUS_KB.values())

st.markdown(
    f'<div class="hero">'
    f'<h1 class="hero-title">Ask your <span class="accent">doubts</span>,<br>'
    f'get expert answers.</h1>'
    f'<p class="hero-sub">'
    f'Professor-quality explanations for every SRM syllabus topic.</p>'
    f'<div class="stats-row">'
    f'<span class="stat-chip">📚 {len(SYLLABUS_KB)} Subjects</span>'
    f'<span class="stat-chip">📅 {len(semesters)} Semesters</span>'
    f'<span class="stat-chip">📝 {topic_count} Topics</span>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)


# ── Chat History ─────────────────────────────────────────────────────────────

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and i in st.session_state.sources_map:
            src = st.session_state.sources_map[i]
            if src:
                st.markdown(format_sources_html(src), unsafe_allow_html=True)


# ── Chat Input ───────────────────────────────────────────────────────────────

if prompt := st.chat_input("What concept would you like to understand?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        sem_filter = selected_sem
        subj_filter = None if selected_subject == "All Subjects" else selected_subject

        with st.spinner("Thinking..."):
            resp_ph = st.empty()
            src_ph = st.empty()

            full_resp = ""
            final_src = []

            for chunk in generate_response_stream(
                query=prompt,
                semester=sem_filter,
                subject=subj_filter,
            ):
                if chunk["type"] == "refusal":
                    full_resp = chunk["content"]
                    resp_ph.markdown(full_resp)
                    break
                elif chunk["type"] == "sources":
                    final_src = chunk["sources"]
                elif chunk["type"] == "token":
                    full_resp += chunk["content"]
                    resp_ph.markdown(full_resp + "●")
                elif chunk["type"] == "done":
                    full_resp = chunk["content"]
                    final_src = chunk.get("sources", final_src)
                    break

            resp_ph.markdown(full_resp)

            if final_src:
                src_ph.markdown(format_sources_html(final_src), unsafe_allow_html=True)

    idx = len(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": full_resp})
    if final_src:
        st.session_state.sources_map[idx] = final_src
