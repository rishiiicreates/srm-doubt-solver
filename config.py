"""
Configuration constants for the SRM College Doubt-Solving Agent.
All system-wide settings are defined here — no magic numbers elsewhere.
"""

import os
import warnings

# Suppress pydantic v1 deprecation warnings on Python 3.14
warnings.filterwarnings("ignore", message=".*Pydantic V1.*Python 3.14.*")

# ── Ollama ────────────────────────────────────────────────────────────────────
OLLAMA_BASE_URL: str = "http://localhost:11434"
LLM_MODEL: str = "llama3"
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

# ── Paths ─────────────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR: str = os.path.join(os.path.dirname(__file__), "vectorstore")
DATA_DIR: str = os.path.join(os.path.dirname(__file__), "data")
MANIFEST_PATH: str = os.path.join(os.path.dirname(__file__), "manifest.json")
CACHE_DIR: str = os.path.join(os.path.dirname(__file__), ".response_cache")

# ── Chunking ──────────────────────────────────────────────────────────────────
CHUNK_SIZE: int = 200          # target tokens per chunk (~1-2 slides)
CHUNK_OVERLAP: int = 30        # token overlap between chunks
MAX_CHUNK_TOKENS: int = 300    # hard ceiling — content above this gets split

# ── Retrieval ─────────────────────────────────────────────────────────────────
TOP_K: int = 5
SIMILARITY_THRESHOLD: float = 0.45   # higher to filter out irrelevant matches

# ── Embedding ─────────────────────────────────────────────────────────────────
EMBEDDING_BATCH_SIZE: int = 32

# ── Caching ───────────────────────────────────────────────────────────────────
CACHE_TTL_SECONDS: int = 86400  # 24 hours

# ── Scraper ───────────────────────────────────────────────────────────────────
HELPERS_BASE_URL: str = "https://thehelpers.vercel.app/"
HELPERS_SEMESTERS_URL: str = "https://thehelpers.vercel.app/semesters"
TOTAL_SEMESTERS: int = 8
REQUEST_DELAY_SECONDS: float = 1.0  # polite scraping delay
MAX_RETRIES: int = 3

# ── ChromaDB ──────────────────────────────────────────────────────────────────
CHROMA_COLLECTION_NAME: str = "srm_syllabus"

# ── LLM ───────────────────────────────────────────────────────────────────────
LLM_TEMPERATURE: float = 0.3
LLM_NUM_CTX: int = 4096

# ── Refusal message (only for truly non-academic queries) ─────────────────────
REFUSAL_MESSAGE: str = (
    "I can only help with academic and study-related questions. "
    "Please ask me about any topic from your syllabus or academics!"
)

# ── System prompt (hardcoded, cannot be overridden) ───────────────────────────
SYSTEM_PROMPT: str = (
    "You are an expert academic doubt-solving assistant for SRM Institute of "
    "Science and Technology. You help students understand ANY academic concept.\n\n"
    "INSTRUCTIONS:\n"
    "1. The CONTEXT below contains syllabus topics that may match the student's "
    "question. These tell you what is officially covered in the SRM curriculum.\n"
    "2. If the context topics DIRECTLY match the student's question, mention the "
    "Subject, Semester, and Unit, then give a DETAILED and COMPREHENSIVE answer. "
    "Include definitions, examples, step-by-step explanations, and real-world "
    "applications.\n"
    "3. If the context topics DO NOT directly match the student's question (the "
    "topics seem unrelated), still give a complete and helpful answer to the "
    "student's question, but add a note at the end: "
    "'Note: This topic does not appear to be directly covered in your current "
    "SRM syllabus, but here is a thorough explanation.'\n"
    "4. Answer as a knowledgeable professor would — be thorough, clear, and "
    "educational. Use bullet points, numbered lists, and examples.\n"
    "5. Do NOT refuse to answer any academic or study-related question. Always "
    "help the student learn.\n"
    "6. Only refuse questions about politics, entertainment, personal advice, "
    "or anything completely unrelated to academics."
)
