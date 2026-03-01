"""
Streamlit Chat UI — SRM College Doubt-Solving Agent.

Premium, polished chat interface with:
  - Sidebar: Dynamic semester/subject filters from syllabus KB
  - Main: Conversational chat with subject-level citations
  - Streaming responses with animated spinner
  - Full 56-subject, 8-semester coverage
"""

import streamlit as st

from config import REFUSAL_MESSAGE
from llm import generate_response_stream
from generate_syllabus_kb import SYLLABUS_KB


# ── Page Configuration ────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SRM Doubt Solver — All Semesters",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Global */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Header */
    .main-header {
        text-align: center;
        padding: 1.2rem 0 0.5rem;
    }
    .main-header h1 {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .main-header p {
        color: #9ca3af;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }
    .header-stats {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-top: 0.5rem;
    }
    .header-stat {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 20px;
        padding: 0.2rem 0.7rem;
        font-size: 0.72rem;
        color: #a5b4fc;
        font-weight: 500;
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 12px !important;
        margin-bottom: 0.5rem;
    }

    /* Sources card */
    .sources-card {
        background: rgba(102, 126, 234, 0.08);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 0.75rem;
    }
    .sources-card h4 {
        color: #667eea;
        margin: 0 0 0.5rem 0;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .source-item {
        background: rgba(255, 255, 255, 0.04);
        border-left: 3px solid #764ba2;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.4rem;
        border-radius: 0 6px 6px 0;
        font-size: 0.82rem;
        color: #d1d5db;
    }
    .source-item strong {
        color: #f093fb;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95);
        backdrop-filter: blur(10px);
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #e2e8f0;
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .status-ok {
        background: rgba(52, 211, 153, 0.15);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }
    .status-warn {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }

    /* Semester tag */
    .sem-tag {
        display: inline-block;
        background: rgba(118, 75, 162, 0.2);
        color: #c4b5fd;
        font-size: 0.65rem;
        padding: 0.1rem 0.4rem;
        border-radius: 8px;
        margin-left: 0.3rem;
        font-weight: 600;
    }

    /* Divider */
    .sidebar-divider {
        border: none;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        margin: 1rem 0;
    }

    /* Subject count */
    .subject-count {
        color: #6b7280;
        font-size: 0.7rem;
        margin-top: -0.5rem;
        margin-bottom: 0.5rem;
    }
</style>
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
    html = '<div class="sources-card"><h4>📚 Sources</h4>'
    for src in sources:
        # Build a dedup key
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
            parts.append(f"<strong>Subject:</strong> {src['subject']}")
        if src.get("semester"):
            parts.append(f"<strong>Semester:</strong> {src['semester']}")

        # Prefer unit_name over unit_number for syllabus KB entries
        unit_name = src.get("unit_name", "")
        if unit_name:
            parts.append(f"<strong>Unit:</strong> {unit_name}")
        elif src.get("unit_number"):
            parts.append(f"<strong>Unit:</strong> {src['unit_number']}")

        if src.get("slide_number") and src.get("slide_number") != 1:
            parts.append(f"<strong>Slide:</strong> {src['slide_number']}")

        # Show filename only for PPT files, not syllabus KB
        filename = src.get("source_filename", "")
        if filename and not filename.startswith("syllabus_"):
            parts.append(f"<strong>File:</strong> {filename}")

        html += f'<div class="source-item">{" &nbsp;│&nbsp; ".join(parts)}</div>'

    html += "</div>"
    return html


# ── Session State Initialization ──────────────────────────────────────────────


if "messages" not in st.session_state:
    st.session_state.messages = []

if "sources_map" not in st.session_state:
    st.session_state.sources_map = {}


# ── Sidebar ──────────────────────────────────────────────────────────────────


with st.sidebar:
    st.markdown("## 🎓 SRM Doubt Solver")
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    # Semester selector — dynamic from syllabus KB
    semesters = get_syllabus_semesters()
    semester_display = ["All Semesters"] + [f"Semester {s}" for s in semesters]

    selected_semester_display = st.selectbox(
        "📅 Select Semester",
        options=semester_display,
        index=0,
        help="Filter answers by semester",
    )

    # Parse selected semester number
    selected_semester_num = None
    if selected_semester_display != "All Semesters":
        selected_semester_num = int(selected_semester_display.split()[-1])

    # Subject selector — dynamic based on semester
    if selected_semester_num is not None:
        subjects = get_subjects_for_semester(selected_semester_num)
    else:
        subjects = get_all_subjects()

    subject_options = ["All Subjects"] + subjects
    selected_subject = st.selectbox(
        "📖 Select Subject",
        options=subject_options,
        index=0,
        help="Filter answers by subject",
    )

    # Show subject count
    if selected_semester_num:
        st.markdown(
            f'<p class="subject-count">{len(subjects)} subjects in Semester {selected_semester_num}</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<p class="subject-count">{len(SYLLABUS_KB)} subjects across {len(semesters)} semesters</p>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    # Status indicators
    from retriever import get_retriever
    try:
        retriever = get_retriever()
        doc_count = retriever.collection_count
        if doc_count > 0:
            st.markdown(
                f'<span class="status-badge status-ok">✓ {doc_count} topics indexed</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="status-badge status-warn">⚠ Run ingest.py first</span>',
                unsafe_allow_html=True,
            )
    except Exception:
        st.markdown(
            '<span class="status-badge status-warn">⚠ Vector store not initialized</span>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.sources_map = {}
        st.rerun()

    # Info
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.caption(
        "Covers all SRM subjects from Semester 1-7. "
        "Ask any syllabus-related doubt!"
    )


# ── Main Chat Area ───────────────────────────────────────────────────────────


# Header
st.markdown(
    '<div class="main-header">'
    '<h1>SRM Doubt Solver</h1>'
    '<p>Your AI study companion for all SRM syllabus topics</p>'
    '<div class="header-stats">'
    f'<span class="header-stat">📚 {len(SYLLABUS_KB)} Subjects</span>'
    f'<span class="header-stat">📅 {len(get_syllabus_semesters())} Semesters</span>'
    f'<span class="header-stat">📝 {sum(len(v["units"]) for v in SYLLABUS_KB.values())} Topics</span>'
    '</div>'
    "</div>",
    unsafe_allow_html=True,
)

# Display chat history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Show sources for assistant messages
        if message["role"] == "assistant" and i in st.session_state.sources_map:
            sources = st.session_state.sources_map[i]
            if sources:
                st.markdown(format_sources_html(sources), unsafe_allow_html=True)


# Chat input
if prompt := st.chat_input("Ask a question about your syllabus..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        # Determine filters
        semester_filter = selected_semester_num
        subject_filter = None
        if selected_subject != "All Subjects":
            subject_filter = selected_subject

        # Stream response
        with st.spinner("🔍 Searching syllabus..."):
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
                    response_placeholder.markdown(full_response + "▌")

                elif chunk["type"] == "done":
                    full_response = chunk["content"]
                    final_sources = chunk.get("sources", final_sources)
                    break

            # Final render (remove cursor)
            response_placeholder.markdown(full_response)

            # Show sources
            if final_sources:
                sources_placeholder.markdown(
                    format_sources_html(final_sources),
                    unsafe_allow_html=True,
                )

    # Save to history
    msg_index = len(st.session_state.messages)
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
    })
    if final_sources:
        st.session_state.sources_map[msg_index] = final_sources
