"""
LLM Configuration & Chain — handles query rewriting, prompt construction,
response generation with Llama 3 via Ollama, and response caching.

The system prompt is HARDCODED and cannot be overridden by user input.
"""

import hashlib
import os
from typing import Generator, Optional

import diskcache
from langchain_ollama import OllamaLLM

from config import (
    CACHE_DIR,
    CACHE_TTL_SECONDS,
    LLM_MODEL,
    LLM_NUM_CTX,
    LLM_TEMPERATURE,
    OLLAMA_BASE_URL,
    REFUSAL_MESSAGE,
    SYSTEM_PROMPT,
)
from retriever import RetrievalResult, retrieve


# ── LLM Instance ─────────────────────────────────────────────────────────────


def create_llm() -> OllamaLLM:
    """Create the Ollama LLM instance with fixed settings."""
    return OllamaLLM(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=LLM_TEMPERATURE,
        num_ctx=LLM_NUM_CTX,
    )


# ── Response Cache ────────────────────────────────────────────────────────────


_cache = diskcache.Cache(CACHE_DIR)


def _cache_key(query: str, semester: Optional[int], subject: Optional[str], chat_history: Optional[list[dict]] = None) -> str:
    """Generate a deterministic cache key from query parameters and history."""
    history_str = str(chat_history) if chat_history else ""
    raw = f"{query}|{semester or ''}|{subject or ''}|{history_str}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached_response(
    query: str,
    semester: Optional[int] = None,
    subject: Optional[str] = None,
    chat_history: Optional[list[dict]] = None,
) -> Optional[dict]:
    """Look up a cached response. Returns None on cache miss."""
    key = _cache_key(query, semester, subject, chat_history)
    result = _cache.get(key)
    return result if result else None


def set_cached_response(
    query: str,
    semester: Optional[int],
    subject: Optional[str],
    response: dict,
    chat_history: Optional[list[dict]] = None,
) -> None:
    """Store a response in the cache with TTL."""
    key = _cache_key(query, semester, subject, chat_history)
    _cache.set(key, response, expire=CACHE_TTL_SECONDS)


# ── Query Rewriter ────────────────────────────────────────────────────────────


def rewrite_query(
    raw_query: str,
    subject: Optional[str] = None,
    semester: Optional[int] = None,
    chat_history: Optional[list[dict]] = None,
) -> str:
    """
    Rewrite an ambiguous student question into a clean retrieval query.

    Uses a lightweight LLM call to rephrase colloquial questions into
    precise academic search queries. When chat history is provided,
    it resolves pronouns and context references.

    Falls back to the original query if rewriting fails.
    """
    # Handle generic/vague queries when a subject is selected
    generic_patterns = [
        "tell me about this subject", "what is this subject", "about this subject",
        "explain this subject", "this subject", "tell me about it", "what is this",
        "explain this", "tell me everything", "overview", "syllabus",
        "what topics", "what all topics", "topics covered",
    ]
    lowered = raw_query.lower().strip()
    if subject and any(pat in lowered for pat in generic_patterns):
        return f"{subject} syllabus topics overview"

    # If subject is selected, prepend it to the query for better retrieval
    enhanced_query = raw_query
    if subject and subject.lower() not in raw_query.lower():
        enhanced_query = f"{subject}: {raw_query}"

    # Skip rewriting for queries that are already clear and academic
    if not chat_history and _is_clear_query(enhanced_query):
        return enhanced_query

    llm = create_llm()

    # Build context-aware rewrite prompt
    context_hint = ""
    if subject and semester:
        context_hint = f"The student is studying '{subject}' (Semester {semester}). "
    elif subject:
        context_hint = f"The student is studying '{subject}'. "

    history_text = ""
    if chat_history:
        history_text = "Recent conversation context:\n"
        for msg in chat_history[-3:]:  # Last 3 messages for context
            role = "Student" if msg["role"] == "user" else "AI"
            history_text += f"{role}: {msg['content']}\n"
        history_text += "\n"

    rewrite_prompt = (
        "You are a search query optimizer for a college syllabus database. "
        f"{context_hint}"
        "Rewrite the following student question into a precise, concise academic "
        "search query. If the student question contains pronouns like 'it', 'this', or refers "
        "to a previous topic, use the conversation context to resolve what they mean in the rewritten query. "
        "Keep subject names, unit numbers, and technical terms. "
        "Remove filler words, slang, and ambiguity. "
        "Return ONLY the rewritten query, nothing else. "
        "Do NOT use placeholders like [Subject Name] — use actual terms.\n\n"
        f"{history_text}"
        f"Student question: {raw_query}\n\n"
        "Rewritten query:"
    )

    try:
        rewritten = llm.invoke(rewrite_prompt).strip().strip('"').strip("'")
        # Sanity checks:
        # - Reasonable length
        # - Not a template (contains [ or ] brackets)
        # - Not identical to the prompt structure
        if (rewritten
            and 3 < len(rewritten) < 200
            and "[" not in rewritten
            and "]" not in rewritten
            and "Subject Name" not in rewritten
            and "Unit Number" not in rewritten):
            # Ensure subject context is in the rewritten query if filter is active
            if subject and subject.lower() not in rewritten.lower():
                rewritten = f"{subject} {rewritten}"
            return rewritten
    except Exception as e:
        print(f"  ⚠ Query rewriting failed: {e}")

    return enhanced_query


def _is_clear_query(query: str) -> bool:
    """Check if a query is already clear enough to skip rewriting."""
    # Already contains academic terms and structure
    words = query.split()
    if len(words) >= 4 and any(
        kw in query.lower()
        for kw in ["explain", "define", "describe", "compare", "difference between",
                    "what is", "what are", "how does", "working principle",
                    "topics covered", "unit"]
    ):
        return True
    return False


# ── Prompt Construction ──────────────────────────────────────────────────────


def build_prompt(
    query: str,
    context: str,
    semester: Optional[int] = None,
    subject: Optional[str] = None,
    chat_history: Optional[list[dict]] = None,
) -> str:
    """
    Build the full prompt with system instructions and context.
    The system prompt is HARDCODED and injected here — it cannot be
    overridden or manipulated by user input.
    """
    # Add filter context so LLM knows what subject/semester the student selected
    filter_note = ""
    if subject and semester:
        filter_note = (
            f"\n\nIMPORTANT: The student is currently studying '{subject}' "
            f"(Semester {semester}). Focus your answer on this subject. "
            f"If the question is about a topic within '{subject}', answer "
            f"specifically for that subject's curriculum."
        )
    elif subject:
        filter_note = (
            f"\n\nIMPORTANT: The student is currently studying '{subject}'. "
            f"Focus your answer on this subject's curriculum."
        )
    elif semester:
        filter_note = (
            f"\n\nIMPORTANT: The student is studying Semester {semester} subjects. "
            f"Focus your answer on topics from this semester."
        )

    if context.strip():
        context_section = (
            "=== OFFICIAL SYLLABUS CONTEXT ===\n\n"
            f"{context}\n\n"
            "=== END OF CONTEXT ==="
        )
    else:
        context_section = (
            "=== OFFICIAL SYLLABUS CONTEXT ===\n\n"
            "No matching syllabus topics were found for this question. "
            "The topic may not be covered in the current SRM syllabus.\n\n"
            "=== END OF CONTEXT ==="
        )

    history_section = ""
    if chat_history:
        history_section = "=== RECENT CONVERSATION HISTORY ===\n\n"
        for msg in chat_history:
            role = "Student" if msg["role"] == "user" else "AI"
            history_section += f"{role}: {msg['content']}\n\n"
        history_section += "=== END OF HISTORY ===\n\n"

    prompt = (
        f"{SYSTEM_PROMPT}{filter_note}\n\n"
        f"{context_section}\n\n"
        f"{history_section}"
        f"Student Question: {query}\n\n"
        "Answer:"
    )
    return prompt


# ── Response Generation ──────────────────────────────────────────────────────


def generate_response(
    query: str,
    semester: Optional[int] = None,
    subject: Optional[str] = None,
    use_cache: bool = True,
    chat_history: Optional[list[dict]] = None,
) -> dict:
    """
    Full RAG pipeline: rewrite query -> retrieve context -> generate answer.

    Args:
        query: The student's question.
        semester: Optional semester filter.
        subject: Optional subject filter.
        use_cache: Whether to check/use the response cache.
        chat_history: List of previous Message dicts for conversational memory.

    Returns:
        Dict with keys: answer, sources, rewritten_query, was_cached, should_refuse
    """
    # Step 1: Rewrite query for better retrieval
    rewritten_query = rewrite_query(query, subject=subject, semester=semester, chat_history=chat_history)

    # Step 2: Check cache
    if use_cache:
        cached = get_cached_response(rewritten_query, semester, subject, chat_history=chat_history)
        if cached:
            cached["was_cached"] = True
            return cached

    # Step 3: Retrieve context
    retrieval_result: RetrievalResult = retrieve(
        query=rewritten_query,
        semester=semester,
        subject=subject,
    )

    # Step 4: Handle refusal (no passing chunks)
    if retrieval_result.should_refuse:
        result = {
            "answer": retrieval_result.refusal_message,
            "sources": [],
            "rewritten_query": rewritten_query,
            "was_cached": False,
            "should_refuse": True,
        }
        return result

    # Step 5: Build prompt with context
    context = retrieval_result.context_text
    prompt = build_prompt(query, context, semester=semester, subject=subject, chat_history=chat_history)

    # Step 6: Generate response
    llm = create_llm()
    try:
        answer = llm.invoke(prompt)
    except Exception as e:
        answer = f"Error generating response: {e}"

    # Step 7: Build sources list
    sources = [
        {
            "slide_number": chunk.slide_number,
            "subject": chunk.subject,
            "unit_name": chunk.unit_name,
            "unit_number": chunk.unit_number,
            "semester": chunk.semester,
            "source_filename": chunk.source_filename,
            "citation": chunk.citation,
            "similarity_score": chunk.similarity_score,
        }
        for chunk in retrieval_result.chunks
    ]

    result = {
        "answer": answer.strip(),
        "sources": sources,
        "rewritten_query": rewritten_query,
        "was_cached": False,
        "should_refuse": False,
    }

    # Step 8: Cache the result
    if use_cache:
        set_cached_response(rewritten_query, semester, subject, result, chat_history=chat_history)

    return result


def generate_response_stream(
    query: str,
    semester: Optional[int] = None,
    subject: Optional[str] = None,
    chat_history: Optional[list[dict]] = None,
) -> Generator[dict, None, None]:
    """
    Streaming version of generate_response.
    Yields partial results as tokens are generated.

    Yields dicts with:
      - type: "token" | "sources" | "refusal" | "done"
      - content: the token text (for type="token")
      - sources: list of source dicts (for type="sources")
      - answer: full answer text (for type="done")
    """
    # Step 1: Rewrite query
    rewritten_query = rewrite_query(query, subject=subject, semester=semester, chat_history=chat_history)

    # Step 2: Check cache
    cached = get_cached_response(rewritten_query, semester, subject, chat_history=chat_history)
    if cached:
        cached["was_cached"] = True
        yield {"type": "done", "content": cached["answer"], "sources": cached.get("sources", []), "was_cached": True}
        return

    # Step 3: Retrieve context
    retrieval_result: RetrievalResult = retrieve(
        query=rewritten_query,
        semester=semester,
        subject=subject,
    )

    # Step 4: Handle refusal
    if retrieval_result.should_refuse:
        yield {"type": "refusal", "content": retrieval_result.refusal_message, "sources": []}
        return

    # Step 5: Yield sources first so UI can display them immediately
    sources = [
        {
            "slide_number": chunk.slide_number,
            "subject": chunk.subject,
            "unit_name": chunk.unit_name,
            "unit_number": chunk.unit_number,
            "semester": chunk.semester,
            "source_filename": chunk.source_filename,
            "citation": chunk.citation,
            "similarity_score": chunk.similarity_score,
        }
        for chunk in retrieval_result.chunks
    ]
    yield {"type": "sources", "content": "", "sources": sources}

    # Step 6: Build prompt and stream response
    context = retrieval_result.context_text
    prompt = build_prompt(query, context, semester=semester, subject=subject, chat_history=chat_history)
    llm = create_llm()

    full_answer = ""
    try:
        for token in llm.stream(prompt):
            full_answer += token
            yield {"type": "token", "content": token, "sources": []}
    except Exception as e:
        error_msg = f"Error generating response: {e}"
        yield {"type": "token", "content": error_msg, "sources": []}
        full_answer = error_msg

    # Step 7: Cache and signal completion
    result = {
        "answer": full_answer.strip(),
        "sources": sources,
        "rewritten_query": rewritten_query,
        "was_cached": False,
        "should_refuse": False,
    }
    set_cached_response(rewritten_query, semester, subject, result, chat_history=chat_history)

    yield {"type": "done", "content": full_answer.strip(), "sources": sources, "was_cached": False}
