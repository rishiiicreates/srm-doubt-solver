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


def _cache_key(query: str, semester: Optional[int], subject: Optional[str]) -> str:
    """Generate a deterministic cache key from query parameters."""
    raw = f"{query}|{semester or ''}|{subject or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached_response(
    query: str,
    semester: Optional[int] = None,
    subject: Optional[str] = None,
) -> Optional[dict]:
    """Look up a cached response. Returns None on cache miss."""
    key = _cache_key(query, semester, subject)
    result = _cache.get(key)
    return result if result else None


def set_cached_response(
    query: str,
    semester: Optional[int],
    subject: Optional[str],
    response: dict,
) -> None:
    """Store a response in the cache with TTL."""
    key = _cache_key(query, semester, subject)
    _cache.set(key, response, expire=CACHE_TTL_SECONDS)


# ── Query Rewriter ────────────────────────────────────────────────────────────


def rewrite_query(raw_query: str) -> str:
    """
    Rewrite an ambiguous student question into a clean retrieval query.

    Uses a lightweight LLM call to rephrase colloquial questions into
    precise academic search queries.

    Examples:
      "what's that theorem in unit 3 circuits?" -> "Thevenin's theorem Unit 3 Circuit Analysis"
      "explain that sorting thing"              -> "sorting algorithms comparison"
      "how do u do trees in ds?"                -> "tree data structure implementation"

    Falls back to the original query if rewriting fails.
    """
    # Skip rewriting for queries that are already clear and academic
    if _is_clear_query(raw_query):
        return raw_query

    llm = create_llm()
    rewrite_prompt = (
        "You are a search query optimizer for a college syllabus database. "
        "Rewrite the following student question into a precise, concise academic "
        "search query. Keep subject names, unit numbers, and technical terms. "
        "Remove filler words, slang, and ambiguity. "
        "Return ONLY the rewritten query, nothing else.\n\n"
        f"Student question: {raw_query}\n\n"
        "Rewritten query:"
    )

    try:
        rewritten = llm.invoke(rewrite_prompt).strip()
        # Sanity check: rewritten query should be reasonable length
        if rewritten and 3 < len(rewritten) < 200:
            return rewritten
    except Exception as e:
        print(f"  ⚠ Query rewriting failed: {e}")

    return raw_query


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


def build_prompt(query: str, context: str) -> str:
    """
    Build the full prompt with system instructions and context.
    The system prompt is HARDCODED and injected here — it cannot be
    overridden or manipulated by user input.
    """
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        "=== OFFICIAL SYLLABUS CONTEXT ===\n\n"
        f"{context}\n\n"
        "=== END OF CONTEXT ===\n\n"
        f"Student Question: {query}\n\n"
        "Answer (cite slide numbers, subject, unit, and semester for every claim):"
    )
    return prompt


# ── Response Generation ──────────────────────────────────────────────────────


def generate_response(
    query: str,
    semester: Optional[int] = None,
    subject: Optional[str] = None,
    use_cache: bool = True,
) -> dict:
    """
    Full RAG pipeline: rewrite query -> retrieve context -> generate answer.

    Args:
        query: The student's question.
        semester: Optional semester filter.
        subject: Optional subject filter.
        use_cache: Whether to check/use the response cache.

    Returns:
        Dict with keys: answer, sources, rewritten_query, was_cached, should_refuse
    """
    # Step 1: Rewrite query for better retrieval
    rewritten_query = rewrite_query(query)

    # Step 2: Check cache
    if use_cache:
        cached = get_cached_response(rewritten_query, semester, subject)
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
    prompt = build_prompt(query, context)

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
        set_cached_response(rewritten_query, semester, subject, result)

    return result


def generate_response_stream(
    query: str,
    semester: Optional[int] = None,
    subject: Optional[str] = None,
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
    rewritten_query = rewrite_query(query)

    # Step 2: Check cache
    cached = get_cached_response(rewritten_query, semester, subject)
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
        }
        for chunk in retrieval_result.chunks
    ]
    yield {"type": "sources", "content": "", "sources": sources}

    # Step 6: Build prompt and stream response
    context = retrieval_result.context_text
    prompt = build_prompt(query, context)
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
    set_cached_response(rewritten_query, semester, subject, result)

    yield {"type": "done", "content": full_answer.strip(), "sources": sources, "was_cached": False}
