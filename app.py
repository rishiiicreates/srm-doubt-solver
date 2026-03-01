"""
Streamlit Chat UI — SRM College Doubt-Solving Agent.

Sarvam.ai-inspired modern design with:
  - Warm gradient backgrounds (orange → peach → lavender)
  - Serif display typography + clean sans-serif body
  - Black pill buttons with inner glow
  - Animated floating particles
  - Glassmorphic cards with rounded corners
  - Generous whitespace and breathing room
"""

import streamlit as st

from config import REFUSAL_MESSAGE
from llm import generate_response_stream
from generate_syllabus_kb import SYLLABUS_KB


# ── Page Configuration ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SRM Doubt Solver — AI Study Companion",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Sarvam-Inspired CSS ──────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap');

    /* ─── Root Variables ─── */
    :root {
        --warm-orange: #FF8C42;
        --soft-peach: #FFAB76;
        --light-lavender: #E8E0F0;
        --pale-blue: #E8EFF9;
        --off-white: #FAFAFA;
        --deep-black: #131313;
        --charcoal: #2D2D2D;
        --warm-gray: #6B6B6B;
        --light-gray: #9CA3AF;
        --accent-indigo: #4F46E5;
        --card-bg: rgba(255, 255, 255, 0.7);
        --glass-border: rgba(255, 255, 255, 0.4);
        --shadow-soft: 0 4px 24px rgba(0, 0, 0, 0.06);
        --shadow-hover: 0 8px 40px rgba(0, 0, 0, 0.1);
    }

    /* ─── Global Background ─── */
    .stApp {
        background: linear-gradient(180deg,
            #FFF3E6 0%,
            #FFE8D6 8%,
            #FFDCC8 15%,
            #F5E6F0 35%,
            #E8EDF8 55%,
            #F0F4FF 75%,
            #FAFBFF 100%
        ) !important;
        font-family: 'Inter', 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ─── Floating Particles Animation ─── */
    @keyframes float-particle {
        0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.4; }
        25% { transform: translateY(-30px) rotate(90deg); opacity: 0.7; }
        50% { transform: translateY(-15px) rotate(180deg); opacity: 0.5; }
        75% { transform: translateY(-40px) rotate(270deg); opacity: 0.6; }
    }

    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(255, 140, 66, 0.15); }
        50% { box-shadow: 0 0 40px rgba(255, 140, 66, 0.25); }
    }

    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    @keyframes fade-up {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes bounce-subtle {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-4px); }
    }

    /* ─── Hero Header ─── */
    .hero-header {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
        animation: fade-up 0.8s ease-out;
        position: relative;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(255, 140, 66, 0.12);
        border: 1px solid rgba(255, 140, 66, 0.25);
        color: var(--warm-orange);
        font-family: 'DM Sans', sans-serif;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        letter-spacing: 0.5px;
        margin-bottom: 1.2rem;
        animation: bounce-subtle 3s ease-in-out infinite;
    }

    .hero-badge .badge-dot {
        width: 6px;
        height: 6px;
        background: var(--warm-orange);
        border-radius: 50%;
        animation: pulse-glow 2s ease-in-out infinite;
    }

    .hero-title {
        font-family: 'Playfair Display', Georgia, serif;
        font-size: 3.2rem;
        font-weight: 700;
        color: var(--deep-black);
        line-height: 1.15;
        margin: 0 0 0.8rem 0;
        letter-spacing: -1px;
    }

    .hero-title .highlight {
        background: linear-gradient(135deg, var(--warm-orange), #E85D75);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        font-family: 'DM Sans', sans-serif;
        color: var(--warm-gray);
        font-size: 1.05rem;
        font-weight: 400;
        line-height: 1.6;
        max-width: 480px;
        margin: 0 auto 1.5rem;
    }

    .hero-stats {
        display: flex;
        justify-content: center;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }

    .stat-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 50px;
        padding: 0.35rem 0.9rem;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--charcoal);
        box-shadow: var(--shadow-soft);
        transition: all 0.3s ease;
    }

    .stat-pill:hover {
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }

    .stat-pill .stat-icon {
        font-size: 0.85rem;
    }

    /* ─── Particle Decorations ─── */
    .particles-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }

    .particle {
        position: absolute;
        border-radius: 50%;
        animation: float-particle 8s ease-in-out infinite;
    }

    .particle:nth-child(1) {
        width: 12px; height: 12px;
        background: rgba(255, 140, 66, 0.2);
        top: 15%; left: 10%;
        animation-delay: 0s;
        animation-duration: 7s;
    }
    .particle:nth-child(2) {
        width: 8px; height: 8px;
        background: rgba(79, 70, 229, 0.15);
        top: 25%; right: 15%;
        animation-delay: 1s;
        animation-duration: 9s;
    }
    .particle:nth-child(3) {
        width: 16px; height: 16px;
        background: rgba(232, 93, 117, 0.12);
        top: 45%; left: 5%;
        animation-delay: 2s;
        animation-duration: 11s;
    }
    .particle:nth-child(4) {
        width: 6px; height: 6px;
        background: rgba(255, 171, 118, 0.25);
        top: 60%; right: 8%;
        animation-delay: 3s;
        animation-duration: 6s;
    }
    .particle:nth-child(5) {
        width: 10px; height: 10px;
        background: rgba(79, 70, 229, 0.1);
        top: 80%; left: 20%;
        animation-delay: 4s;
        animation-duration: 10s;
    }
    .particle:nth-child(6) {
        width: 14px; height: 14px;
        background: rgba(255, 140, 66, 0.1);
        top: 35%; right: 25%;
        animation-delay: 1.5s;
        animation-duration: 8s;
    }

    /* ─── Chat Messages ─── */
    .stChatMessage {
        border-radius: 16px !important;
        margin-bottom: 0.75rem;
        backdrop-filter: blur(8px);
        animation: fade-up 0.4s ease-out;
    }

    [data-testid="stChatMessageContent"] {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.95rem;
        line-height: 1.7;
        color: var(--charcoal);
    }

    /* ─── Sources Card ─── */
    .sources-card {
        background: var(--card-bg);
        backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.2rem;
        margin-top: 1rem;
        box-shadow: var(--shadow-soft);
        animation: fade-up 0.5s ease-out;
    }

    .sources-card h4 {
        font-family: 'DM Sans', sans-serif;
        color: var(--warm-orange);
        margin: 0 0 0.75rem 0;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    .sources-card h4::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, rgba(255, 140, 66, 0.3), transparent);
        margin-left: 0.5rem;
    }

    .source-item {
        background: rgba(255, 255, 255, 0.5);
        border-left: 3px solid var(--warm-orange);
        padding: 0.6rem 0.9rem;
        margin-bottom: 0.5rem;
        border-radius: 0 10px 10px 0;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.8rem;
        color: var(--charcoal);
        transition: all 0.25s ease;
    }

    .source-item:hover {
        background: rgba(255, 140, 66, 0.06);
        transform: translateX(4px);
        border-left-color: #E85D75;
    }

    .source-item strong {
        color: var(--warm-orange);
        font-weight: 600;
    }

    /* ─── Sidebar ─── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFF8F0 0%, #FFF3E6 40%, #F5EFF8 100%) !important;
        border-right: 1px solid rgba(255, 140, 66, 0.1);
    }

    section[data-testid="stSidebar"] .stSelectbox label {
        font-family: 'DM Sans', sans-serif;
        font-weight: 600;
        color: var(--charcoal) !important;
        font-size: 0.85rem;
    }

    section[data-testid="stSidebar"] h2 {
        font-family: 'Playfair Display', serif !important;
        color: var(--deep-black) !important;
        font-size: 1.3rem !important;
    }

    /* ─── Sidebar Branding Area ─── */
    .sidebar-brand {
        text-align: center;
        padding: 1rem 0 0.5rem;
    }

    .sidebar-logo {
        font-family: 'Playfair Display', serif;
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--deep-black);
        margin: 0;
        letter-spacing: -0.5px;
    }

    .sidebar-tagline {
        font-family: 'DM Sans', sans-serif;
        color: var(--warm-gray);
        font-size: 0.72rem;
        margin-top: 0.15rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* ─── Status Badge ─── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.3rem 0.75rem;
        border-radius: 50px;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.72rem;
        font-weight: 600;
    }

    .status-ok {
        background: rgba(34, 197, 94, 0.1);
        color: #16a34a;
        border: 1px solid rgba(34, 197, 94, 0.2);
    }

    .status-ok .pulse-dot {
        width: 6px;
        height: 6px;
        background: #16a34a;
        border-radius: 50%;
        display: inline-block;
        animation: pulse-glow 2s ease-in-out infinite;
    }

    .status-warn {
        background: rgba(245, 158, 11, 0.1);
        color: #d97706;
        border: 1px solid rgba(245, 158, 11, 0.2);
    }

    /* ─── Sidebar Subject Count ─── */
    .subject-count {
        font-family: 'DM Sans', sans-serif;
        color: var(--light-gray);
        font-size: 0.7rem;
        margin-top: -0.3rem;
        margin-bottom: 0.5rem;
    }

    /* ─── Divider ─── */
    .sidebar-divider {
        border: none;
        border-top: 1px solid rgba(255, 140, 66, 0.12);
        margin: 1rem 0;
    }

    /* ─── Footer Caption ─── */
    .sidebar-footer {
        font-family: 'DM Sans', sans-serif;
        color: var(--light-gray);
        font-size: 0.7rem;
        text-align: center;
        line-height: 1.5;
        padding: 0 0.5rem;
    }

    /* ─── Selectbox + Input Styling ─── */
    .stSelectbox > div > div {
        border-radius: 12px !important;
        border-color: rgba(255, 140, 66, 0.2) !important;
        font-family: 'DM Sans', sans-serif !important;
        background: rgba(255, 255, 255, 0.7) !important;
    }

    .stSelectbox > div > div:hover {
        border-color: var(--warm-orange) !important;
    }

    /* Chat input */
    .stChatInput {
        border-radius: 50px !important;
    }

    .stChatInput > div {
        border-radius: 50px !important;
        border: 2px solid rgba(255, 140, 66, 0.15) !important;
        background: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        box-shadow: 0 2px 16px rgba(0, 0, 0, 0.04) !important;
        transition: all 0.3s ease !important;
        padding: 0.15rem 0.25rem !important;
    }

    .stChatInput > div:focus-within {
        border-color: var(--warm-orange) !important;
        box-shadow: 0 4px 24px rgba(255, 140, 66, 0.12) !important;
    }

    /* Send button — black pill style */
    .stChatInput button {
        background: var(--deep-black) !important;
        border-radius: 50px !important;
        color: white !important;
        box-shadow: inset 0 0 12px rgba(255, 255, 255, 0.15) !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }

    .stChatInput button:hover {
        background: var(--charcoal) !important;
        box-shadow: inset 0 0 16px rgba(255, 255, 255, 0.2),
                    0 4px 16px rgba(0, 0, 0, 0.15) !important;
        transform: scale(1.05);
    }

    /* ─── Button Styling (Clear Chat) ─── */
    .stButton > button {
        background: var(--deep-black) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        padding: 0.5rem 1.5rem !important;
        box-shadow: inset 0 0 12px rgba(255, 255, 255, 0.1) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    .stButton > button:hover {
        background: var(--charcoal) !important;
        box-shadow: inset 0 0 16px rgba(255, 255, 255, 0.15),
                    0 6px 24px rgba(0, 0, 0, 0.12) !important;
        transform: translateY(-2px) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* ─── Spinner ─── */
    .stSpinner > div {
        border-color: var(--warm-orange) transparent transparent transparent !important;
    }

    /* ─── Hide Streamlit defaults ─── */
    .stDeployButton { display: none !important; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* ─── Scrollbar ─── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 140, 66, 0.2);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 140, 66, 0.35);
    }
</style>
""", unsafe_allow_html=True)


# ── Floating Particles (background decoration) ───────────────────────────────

st.markdown("""
<div class="particles-container">
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
</div>
""", unsafe_allow_html=True)


# ── Helper Functions ──────────────────────────────────────────────────────────


def get_syllabus_semesters() -> list[int]:
    """Get sorted list of unique semesters from the syllabus KB."""
    return sorted(set(info["semester"] for info in SYLLABUS_KB.values()))


def get_subjects_for_semester(semester: int) -> list[str]:
    """Get subjects for a specific semester from the syllabus KB."""
    return sorted(
        name for name, info in SYLLABUS_KB.items()
        if info["semester"] == semester
    )


def get_all_subjects() -> list[str]:
    """Get all subjects from the syllabus KB."""
    return sorted(SYLLABUS_KB.keys())


def format_sources_html(sources: list[dict]) -> str:
    """Format source citations as styled HTML with unit names."""
    if not sources:
        return ""

    seen = set()
    html = '<div class="sources-card"><h4>Referenced Topics</h4>'
    for src in sources:
        key = (
            src.get("subject", ""),
            src.get("semester", ""),
            src.get("unit_name", src.get("unit_number", "")),
        )
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

        filename = src.get("source_filename", "")
        if filename and not filename.startswith("syllabus_"):
            parts.append(f"📄 {filename}")

        html += f'<div class="source-item">{" &nbsp;·&nbsp; ".join(parts)}</div>'

    html += "</div>"
    return html


# ── Session State ─────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "sources_map" not in st.session_state:
    st.session_state.sources_map = {}


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        '<div class="sidebar-brand">'
        '<p class="sidebar-logo">SRM Doubt Solver</p>'
        '<p class="sidebar-tagline">AI Study Companion</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    # Semester selector
    semesters = get_syllabus_semesters()
    semester_display = ["All Semesters"] + [f"Semester {s}" for s in semesters]

    selected_semester_display = st.selectbox(
        "📅 Semester",
        options=semester_display,
        index=0,
        help="Filter answers by semester",
    )

    selected_semester_num = None
    if selected_semester_display != "All Semesters":
        selected_semester_num = int(selected_semester_display.split()[-1])

    # Subject selector
    if selected_semester_num is not None:
        subjects = get_subjects_for_semester(selected_semester_num)
    else:
        subjects = get_all_subjects()

    subject_options = ["All Subjects"] + subjects
    selected_subject = st.selectbox(
        "📖 Subject",
        options=subject_options,
        index=0,
        help="Filter answers by subject",
    )

    if selected_semester_num:
        st.markdown(
            f'<p class="subject-count">{len(subjects)} subjects in Sem {selected_semester_num}</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<p class="subject-count">{len(SYLLABUS_KB)} subjects · {len(semesters)} semesters</p>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    # Status
    from retriever import get_retriever
    try:
        retriever = get_retriever()
        doc_count = retriever.collection_count
        if doc_count > 0:
            st.markdown(
                f'<span class="status-badge status-ok">'
                f'<span class="pulse-dot"></span> {doc_count} topics indexed</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="status-badge status-warn">⚠ Run ingest.py first</span>',
                unsafe_allow_html=True,
            )
    except Exception:
        st.markdown(
            '<span class="status-badge status-warn">⚠ Not initialized</span>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sources_map = {}
        st.rerun()

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.markdown(
        '<p class="sidebar-footer">'
        'Powered by Llama 3 · Covers Semester 1–7<br>'
        'Ask any syllabus-related doubt'
        '</p>',
        unsafe_allow_html=True,
    )


# ── Hero Header ──────────────────────────────────────────────────────────────

topic_count = sum(len(v["units"]) for v in SYLLABUS_KB.values())

st.markdown(
    f'<div class="hero-header">'
    f'<div class="hero-badge"><span class="badge-dot"></span> AI-Powered Study Companion</div>'
    f'<h1 class="hero-title">Ask your <span class="highlight">doubts</span>,<br>'
    f'get expert answers</h1>'
    f'<p class="hero-subtitle">'
    f'Covers every subject in the SRM syllabus. '
    f'Get detailed, professor-quality explanations instantly.</p>'
    f'<div class="hero-stats">'
    f'<span class="stat-pill"><span class="stat-icon">📚</span> {len(SYLLABUS_KB)} Subjects</span>'
    f'<span class="stat-pill"><span class="stat-icon">📅</span> {len(semesters)} Semesters</span>'
    f'<span class="stat-pill"><span class="stat-icon">📝</span> {topic_count} Topics</span>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)


# ── Chat History ─────────────────────────────────────────────────────────────

for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and i in st.session_state.sources_map:
            sources = st.session_state.sources_map[i]
            if sources:
                st.markdown(format_sources_html(sources), unsafe_allow_html=True)


# ── Chat Input ───────────────────────────────────────────────────────────────

if prompt := st.chat_input("What concept would you like to understand?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        semester_filter = selected_semester_num
        subject_filter = None
        if selected_subject != "All Subjects":
            subject_filter = selected_subject

        with st.spinner("Finding the best explanation..."):
            response_placeholder = st.empty()
            sources_placeholder = st.empty()

            full_response = ""
            final_sources = []

            for chunk in generate_response_stream(
                query=prompt,
                semester=semester_filter,
                subject=subject_filter,
            ):
                if chunk["type"] == "refusal":
                    full_response = chunk["content"]
                    response_placeholder.markdown(full_response)
                    break

                elif chunk["type"] == "sources":
                    final_sources = chunk["sources"]

                elif chunk["type"] == "token":
                    full_response += chunk["content"]
                    response_placeholder.markdown(full_response + "●")

                elif chunk["type"] == "done":
                    full_response = chunk["content"]
                    final_sources = chunk.get("sources", final_sources)
                    break

            response_placeholder.markdown(full_response)

            if final_sources:
                sources_placeholder.markdown(
                    format_sources_html(final_sources),
                    unsafe_allow_html=True,
                )

    msg_index = len(st.session_state.messages)
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
    })
    if final_sources:
        st.session_state.sources_map[msg_index] = final_sources
