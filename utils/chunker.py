"""
Intelligent Chunker — splits slide content into retrieval-ready chunks
using a token-aware sliding window that respects slide boundaries.

Strategy:
  - Target chunk size: 500-800 tokens (configurable via config.CHUNK_SIZE)
  - Overlap: 100 tokens between consecutive chunks
  - Never splits a single slide across chunks UNLESS it exceeds MAX_CHUNK_TOKENS
  - Preserves all metadata through chunking
  - Returns LangChain Document objects
"""

import tiktoken
from langchain_core.documents import Document

from config import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CHUNK_TOKENS


# Use cl100k_base tokenizer (GPT-4 / general purpose)
_ENCODER = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Count the number of tokens in a text string."""
    return len(_ENCODER.encode(text))


def _split_text_by_tokens(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    """
    Split a long text into chunks of at most max_tokens with overlap.
    Uses token-level splitting for precision.
    """
    tokens = _ENCODER.encode(text)
    if len(tokens) <= max_tokens:
        return [text]

    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = _ENCODER.decode(chunk_tokens)
        chunks.append(chunk_text)

        # Advance by (max_tokens - overlap) to create overlap
        start += max_tokens - overlap_tokens
        if start >= len(tokens):
            break

    return chunks


def chunk_slides(slides: list[Document]) -> list[Document]:
    """
    Chunk a list of slide Documents using a sliding-window strategy
    that respects slide boundaries.

    Each input Document represents a single slide with metadata including
    at minimum: semester, subject, unit_number, slide_number, source_filename.

    Strategy:
    1. If a single slide fits within CHUNK_SIZE tokens, accumulate slides
       into a buffer until adding the next slide would exceed CHUNK_SIZE.
    2. When the buffer would overflow, emit the current buffer as a chunk.
    3. Apply CHUNK_OVERLAP by keeping the tail tokens of the previous chunk
       in the overlap buffer.
    4. If a single slide exceeds MAX_CHUNK_TOKENS, force-split it with overlap.

    Returns:
        List of chunked Document objects with preserved metadata.
    """
    if not slides:
        return []

    chunks = []
    buffer_texts: list[str] = []
    buffer_tokens: int = 0
    buffer_metadata: dict = {}
    buffer_slide_numbers: list[int] = []

    for slide in slides:
        slide_text = slide.page_content.strip()
        if not slide_text:
            continue

        slide_tokens = count_tokens(slide_text)
        slide_meta = slide.metadata.copy()
        slide_num = slide_meta.get("slide_number", 0)

        # Case 1: Single slide exceeds MAX_CHUNK_TOKENS — force split
        if slide_tokens > MAX_CHUNK_TOKENS:
            # First, flush the current buffer
            if buffer_texts:
                chunks.append(_make_chunk(buffer_texts, buffer_metadata, buffer_slide_numbers))
                buffer_texts = []
                buffer_tokens = 0
                buffer_slide_numbers = []

            # Split the oversized slide
            sub_chunks = _split_text_by_tokens(slide_text, CHUNK_SIZE, CHUNK_OVERLAP)
            for i, sub_text in enumerate(sub_chunks):
                meta = slide_meta.copy()
                meta["chunk_part"] = i + 1
                meta["total_parts"] = len(sub_chunks)
                chunks.append(Document(page_content=sub_text, metadata=meta))

            continue

        # Case 2: Adding this slide would exceed CHUNK_SIZE — flush buffer
        if buffer_tokens + slide_tokens > CHUNK_SIZE and buffer_texts:
            chunks.append(_make_chunk(buffer_texts, buffer_metadata, buffer_slide_numbers))

            # Apply overlap: keep tail of previous content
            overlap_text = _get_overlap_text("\n\n".join(buffer_texts), CHUNK_OVERLAP)
            buffer_texts = [overlap_text] if overlap_text else []
            buffer_tokens = count_tokens(overlap_text) if overlap_text else 0
            buffer_slide_numbers = []
            buffer_metadata = {}

        # Add slide to buffer
        buffer_texts.append(slide_text)
        buffer_tokens += slide_tokens
        buffer_slide_numbers.append(slide_num)

        # Keep metadata from the first slide in the chunk as the primary reference
        if not buffer_metadata:
            buffer_metadata = slide_meta.copy()

    # Flush remaining buffer
    if buffer_texts:
        chunks.append(_make_chunk(buffer_texts, buffer_metadata, buffer_slide_numbers))

    return chunks


def _make_chunk(texts: list[str], metadata: dict, slide_numbers: list[int]) -> Document:
    """Create a Document chunk from accumulated texts and metadata."""
    content = "\n\n".join(texts)
    meta = metadata.copy()

    # Record all slide numbers covered by this chunk
    valid_slides = [s for s in slide_numbers if s > 0]
    if valid_slides:
        meta["slide_number"] = valid_slides[0]  # Primary slide
        meta["slides_covered"] = valid_slides    # All slides in chunk

    return Document(page_content=content, metadata=meta)


def _get_overlap_text(text: str, overlap_tokens: int) -> str:
    """Extract the last `overlap_tokens` tokens from text as overlap."""
    tokens = _ENCODER.encode(text)
    if len(tokens) <= overlap_tokens:
        return text
    overlap = tokens[-overlap_tokens:]
    return _ENCODER.decode(overlap)


def chunk_documents(documents: list[Document]) -> list[Document]:
    """
    High-level chunking entry point.

    Groups documents by source file, then chunks each file's slides
    independently to maintain per-file slide boundary integrity.

    Args:
        documents: List of Documents (one per slide/page) with metadata.

    Returns:
        Chunked Documents ready for embedding.
    """
    # Group by source file to respect per-file slide boundaries
    file_groups: dict[str, list[Document]] = {}
    for doc in documents:
        key = doc.metadata.get("source_filename", "unknown")
        if key not in file_groups:
            file_groups[key] = []
        file_groups[key].append(doc)

    all_chunks = []
    for filename, slides in file_groups.items():
        # Sort by slide number within each file
        slides.sort(key=lambda d: d.metadata.get("slide_number", 0))
        chunks = chunk_slides(slides)
        all_chunks.extend(chunks)

    print(f"  📦 Chunked {len(documents)} slides into {len(all_chunks)} chunks")
    return all_chunks
