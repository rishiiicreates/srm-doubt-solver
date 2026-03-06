"""
Retriever — performs similarity search against ChromaDB with optional
metadata filtering, enforces the 0.45 similarity threshold, and returns
structured results with full citation metadata.
"""

import json
from dataclasses import dataclass, field
from typing import Optional

import chromadb
from langchain_ollama import OllamaEmbeddings

from config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    REFUSAL_MESSAGE,
    SIMILARITY_THRESHOLD,
    TOP_K,
)


# ── Result Data Classes ──────────────────────────────────────────────────────


@dataclass
class RetrievedChunk:
    """A single retrieved chunk with its metadata and score."""
    content: str
    similarity_score: float
    semester: int = 0
    subject: str = ""
    unit_name: str = ""
    unit_number: int = 0
    slide_number: int = 0
    source_filename: str = ""
    source_url: str = ""
    slides_covered: list = field(default_factory=list)

    @property
    def citation(self) -> str:
        """Format a human-readable citation string."""
        parts = []
        if self.subject:
            parts.append(f"Subject: {self.subject}")
        if self.semester:
            parts.append(f"Semester: {self.semester}")
        if self.unit_number:
            parts.append(f"Unit: {self.unit_number}")
        if self.slide_number:
            parts.append(f"Slide: {self.slide_number}")
        if self.source_filename:
            parts.append(f"Source: {self.source_filename}")
        return " | ".join(parts) if parts else "No citation available"


@dataclass
class RetrievalResult:
    """Result of a retrieval query."""
    chunks: list[RetrievedChunk] = field(default_factory=list)
    query: str = ""
    should_refuse: bool = False
    refusal_message: str = REFUSAL_MESSAGE

    @property
    def has_context(self) -> bool:
        """Whether there are any passing chunks to use as context."""
        return len(self.chunks) > 0 and not self.should_refuse

    @property
    def context_text(self) -> str:
        """Format all passing chunks into a context string for the LLM."""
        if not self.has_context:
            return ""

        context_parts = []
        for i, chunk in enumerate(self.chunks, 1):
            header = f"[Source {i}: {chunk.citation}]"
            context_parts.append(f"{header}\n{chunk.content}")

        return "\n\n---\n\n".join(context_parts)


# ── Retriever Class ──────────────────────────────────────────────────────────


class SyllabusRetriever:
    """
    Retrieves relevant syllabus chunks from ChromaDB with metadata filtering
    and similarity threshold enforcement.
    """

    def __init__(self):
        """Initialize the retriever with ChromaDB client and embeddings."""
        self._client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self._collection = self._client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self._embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL,
        )

    @property
    def collection_count(self) -> int:
        """Number of documents in the collection."""
        return self._collection.count()

    def retrieve(
        self,
        query: str,
        semester: Optional[int] = None,
        subject: Optional[str] = None,
        top_k: int = TOP_K,
        threshold: float = SIMILARITY_THRESHOLD,
    ) -> RetrievalResult:
        """
        Retrieve the most relevant chunks for a query.

        Args:
            query: The student's question (or rewritten query).
            semester: Optional semester filter (1-8).
            subject: Optional subject name filter.
            top_k: Number of chunks to retrieve before filtering.
            threshold: Minimum similarity score (0-1). Chunks below this are discarded.

        Returns:
            RetrievalResult with passing chunks or refusal signal.
        """
        if self.collection_count == 0:
            return RetrievalResult(
                query=query,
                should_refuse=True,
                refusal_message="No syllabus data has been indexed yet. Please run the ingestion pipeline first.",
            )

        # Build metadata filter
        where_filter = self._build_filter(semester, subject)

        # Generate query embedding
        try:
            query_embedding = self._embeddings.embed_query(query)
        except Exception as e:
            print(f"  ❌ Embedding query failed: {e}")
            return RetrievalResult(
                query=query,
                should_refuse=True,
                refusal_message="Failed to process your question. Please try again.",
            )

        # Perform similarity search
        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self.collection_count),
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            print(f"  ❌ ChromaDB query failed: {e}")
            return RetrievalResult(
                query=query,
                should_refuse=True,
                refusal_message="Database query failed. Please ensure the vector store is properly initialized.",
            )

        # Process results
        chunks = self._process_results(results, threshold)

        # ── Precision filter: keep only genuinely relevant chunks  ───
        chunks = self._precision_filter(chunks, query)

        # If filters are active but no chunks match, give a helpful refusal
        if not chunks and (semester or subject):
            filter_desc = []
            if subject:
                filter_desc.append(f"subject '{subject}'")
            if semester:
                filter_desc.append(f"Semester {semester}")
            filter_str = " in ".join(filter_desc)
            return RetrievalResult(
                chunks=[],
                query=query,
                should_refuse=False,  # Don't refuse, let LLM answer but note it
                refusal_message="",
            )

        return RetrievalResult(
            chunks=chunks,
            query=query,
            should_refuse=False,
        )

    def _precision_filter(
        self,
        chunks: list[RetrievedChunk],
        query: str,
    ) -> list[RetrievedChunk]:
        """
        Precision filter to ensure only genuinely relevant
        chunks appear in the source references.

        Gap filter: Only keep chunks within 1.5% similarity
        of the best match.
        Subject isolation: Only keep chunks from the top-scoring subject.
        """
        if not chunks:
            return chunks

        # Sort by similarity (highest first)
        chunks.sort(key=lambda c: c.similarity_score, reverse=True)

        # Gap filter
        best_score = chunks[0].similarity_score
        gap_cutoff = best_score - 0.015
        chunks = [c for c in chunks if c.similarity_score >= gap_cutoff]

        # Subject isolation filter
        # If we have a decent match, don't mix subjects (e.g. don't mix Math and CS)
        if best_score > 0.50:
            top_subject = chunks[0].subject
            if top_subject:
                chunks = [c for c in chunks if c.subject == top_subject]

        return chunks

    def _build_filter(
        self,
        semester: Optional[int],
        subject: Optional[str],
    ) -> Optional[dict]:
        """Build ChromaDB 'where' filter from optional parameters."""
        conditions = []

        if semester is not None and semester > 0:
            conditions.append({"semester": {"$eq": semester}})

        if subject is not None and subject.strip():
            conditions.append({"subject": {"$eq": subject}})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}

    def _process_results(
        self,
        results: dict,
        threshold: float,
    ) -> list[RetrievedChunk]:
        """
        Process raw ChromaDB results into RetrievedChunk objects,
        filtering by similarity threshold.

        ChromaDB returns distances (lower = more similar for cosine).
        Cosine distance = 1 - cosine_similarity, so:
        similarity = 1 - distance
        """
        chunks = []

        if not results or not results.get("documents"):
            return chunks

        documents = results["documents"][0]  # First (only) query
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for doc, meta, distance in zip(documents, metadatas, distances):
            # Convert cosine distance to similarity score
            similarity = 1.0 - distance

            # Apply threshold filter
            if similarity < threshold:
                continue

            # Parse slides_covered if it's a JSON string
            slides_covered = meta.get("slides_covered", "[]")
            if isinstance(slides_covered, str):
                try:
                    slides_covered = json.loads(slides_covered)
                except (json.JSONDecodeError, TypeError):
                    slides_covered = []

            chunk = RetrievedChunk(
                content=doc,
                similarity_score=round(similarity, 4),
                semester=int(meta.get("semester", 0)),
                subject=str(meta.get("subject", "")),
                unit_name=str(meta.get("unit_name", "")),
                unit_number=int(meta.get("unit_number", 0)),
                slide_number=int(meta.get("slide_number", 0)),
                source_filename=str(meta.get("source_filename", "")),
                source_url=str(meta.get("source_url", "")),
                slides_covered=slides_covered,
            )
            chunks.append(chunk)

        # Sort by similarity (highest first)
        chunks.sort(key=lambda c: c.similarity_score, reverse=True)

        return chunks


# ── Module-level convenience ─────────────────────────────────────────────────


_retriever_instance: Optional[SyllabusRetriever] = None


def get_retriever() -> SyllabusRetriever:
    """Get or create a singleton retriever instance."""
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = SyllabusRetriever()
    return _retriever_instance


def retrieve(
    query: str,
    semester: Optional[int] = None,
    subject: Optional[str] = None,
) -> RetrievalResult:
    """
    Convenience function for retrieval.

    Args:
        query: The student's question.
        semester: Optional semester filter.
        subject: Optional subject filter.

    Returns:
        RetrievalResult with chunks or refusal signal.
    """
    retriever = get_retriever()
    return retriever.retrieve(query, semester=semester, subject=subject)
