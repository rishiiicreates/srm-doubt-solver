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
EMBEDDING_MODEL: str = "nomic-embed-text"

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
TOP_K: int = 8
SIMILARITY_THRESHOLD: float = 0.3

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

# ── Refusal message (single source of truth) ─────────────────────────────────
REFUSAL_MESSAGE: str = (
    "This topic is not covered in the official syllabus materials."
)

# ── System prompt (hardcoded, cannot be overridden) ───────────────────────────
SYSTEM_PROMPT: str = (
    "You are an expert academic doubt-solving assistant for SRM Institute of "
    "Science and Technology. Your role is to help students understand concepts "
    "from their official syllabus across all semesters and subjects.\n\n"
    "INSTRUCTIONS:\n"
    "1. The CONTEXT below tells you which syllabus topics match the student's "
    "question. Use this to verify the topic is part of the SRM curriculum.\n"
    "2. If the context matches the question, provide a DETAILED and COMPREHENSIVE "
    "answer explaining the concept thoroughly. Include definitions, examples, "
    "diagrams described in text, step-by-step explanations, and real-world "
    "applications where relevant.\n"
    "3. Always mention which Subject, Semester, and Unit the topic belongs to, "
    "based on the context provided.\n"
    "4. If NONE of the context topics match the student's question, respond with "
    "exactly: This topic is not covered in the official syllabus materials.\n"
    "5. Answer as a knowledgeable professor would — be thorough, clear, and "
    "educational. Use bullet points, numbered lists, and examples.\n"
    "6. Do NOT answer questions about politics, entertainment, personal advice, "
    "or anything unrelated to academics."
)
