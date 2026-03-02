"""
Ingestion Pipeline — scrapes, downloads, loads, chunks, embeds, and stores
all SRM syllabus PPT files into a persistent ChromaDB vector database.

Usage:
  python ingest.py             # Normal run (skips unchanged files)
  python ingest.py --reindex   # Force full reprocessing
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredPowerPointLoader
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb

from config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    DATA_DIR,
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_MODEL,
    MANIFEST_PATH,
)
from utils.downloader import scrape_and_download, load_manifest, _md5
from utils.metadata_extractor import extract_metadata_from_path, enrich_metadata
from utils.chunker import chunk_documents


# ── File Discovery ────────────────────────────────────────────────────────────


def discover_ppt_files(data_dir: str) -> list[str]:
    """
    Recursively discover all .ppt and .pptx files in the data directory.

    Returns:
        List of absolute file paths.
    """
    ppt_files = []
    for root, _dirs, files in os.walk(data_dir):
        for f in files:
            if f.lower().endswith((".ppt", ".pptx")):
                ppt_files.append(os.path.join(root, f))

    ppt_files.sort()
    return ppt_files


# ── Hash-Based Deduplication ──────────────────────────────────────────────────


def load_ingestion_state() -> dict:
    """Load the ingestion state (file hashes) from disk."""
    state_path = os.path.join(CHROMA_PERSIST_DIR, "ingestion_state.json")
    if os.path.exists(state_path):
        with open(state_path, "r") as f:
            return json.load(f)
    return {"file_hashes": {}}


def save_ingestion_state(state: dict) -> None:
    """Save ingestion state to disk."""
    os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
    state_path = os.path.join(CHROMA_PERSIST_DIR, "ingestion_state.json")
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)


def compute_file_hash(filepath: str) -> str:
    """Compute MD5 hash of a file."""
    return _md5(filepath)


# ── PPT Loading ───────────────────────────────────────────────────────────────


def load_ppt_file(filepath: str) -> list[Document]:
    """
    Load a single PPT/PPTX file using UnstructuredPowerPointLoader.
    Extracts slide body text and speaker notes per slide.

    Returns:
        List of Documents, one per slide/element.
    """
    try:
        # mode="elements" gives us per-slide/per-element granularity
        loader = UnstructuredPowerPointLoader(filepath, mode="elements")
        documents = loader.load()

        if not documents:
            # Fallback to single-document mode
            loader = UnstructuredPowerPointLoader(filepath, mode="single")
            documents = loader.load()

        return documents

    except Exception as e:
        print(f"  ⚠ Failed to load {filepath}: {e}")
        return []


def load_and_tag_documents(ppt_files: list[str], manifest_data: dict | None = None) -> list[Document]:
    """
    Load all PPT files and tag each document with metadata.

    Args:
        ppt_files: List of file paths to load.
        manifest_data: Loaded manifest for URL cross-referencing.

    Returns:
        List of tagged Documents (one per slide/element).
    """
    all_documents = []

    for filepath in ppt_files:
        print(f"\n  📄 Loading: {os.path.basename(filepath)}")

        # Extract base metadata from file path
        base_meta = extract_metadata_from_path(filepath)
        base_meta["source_filepath"] = filepath

        # Load the PPT
        raw_docs = load_ppt_file(filepath)

        if not raw_docs:
            print(f"    ⚠ No content extracted from {os.path.basename(filepath)}")
            continue

        print(f"    📃 Extracted {len(raw_docs)} elements")

        # Tag each document with enriched metadata
        for i, doc in enumerate(raw_docs):
            enriched_meta = enrich_metadata(
                base_metadata=base_meta,
                page_index=i,
                content=doc.page_content,
                manifest_data=manifest_data,
            )
            # Merge with any existing metadata from the loader
            doc.metadata.update(enriched_meta)
            all_documents.append(doc)

    return all_documents


# ── Embedding & Storage ──────────────────────────────────────────────────────


def create_embeddings_model() -> HuggingFaceEmbeddings:
    """Create the HuggingFace embeddings model."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


def store_in_chromadb(chunks: list[Document], embeddings_model: HuggingFaceEmbeddings) -> None:
    """
    Generate embeddings in batches and store in ChromaDB.

    Args:
        chunks: Chunked documents with metadata.
        embeddings_model: Ollama embeddings model instance.
    """
    if not chunks:
        print("  ℹ No chunks to store.")
        return

    # Initialize ChromaDB persistent client
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    # Get or create collection
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    total = len(chunks)
    print(f"\n  🔢 Embedding and storing {total} chunks in batches of {EMBEDDING_BATCH_SIZE}...")

    for batch_start in range(0, total, EMBEDDING_BATCH_SIZE):
        batch_end = min(batch_start + EMBEDDING_BATCH_SIZE, total)
        batch = chunks[batch_start:batch_end]

        texts = [doc.page_content for doc in batch]
        metadatas = []
        for doc in batch:
            # ChromaDB requires metadata values to be str, int, float, or bool
            clean_meta = {}
            for k, v in doc.metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                elif isinstance(v, list):
                    clean_meta[k] = json.dumps(v)
                elif v is None:
                    clean_meta[k] = ""
                else:
                    clean_meta[k] = str(v)
            metadatas.append(clean_meta)

        # Generate embeddings for the batch
        try:
            embeddings = embeddings_model.embed_documents(texts)
        except Exception as e:
            print(f"  ❌ Embedding batch {batch_start}-{batch_end} failed: {e}")
            continue

        # Generate unique IDs for each chunk
        ids = [
            f"{doc.metadata.get('source_filename', 'unknown')}_{doc.metadata.get('slide_number', 0)}_{batch_start + i}"
            for i, doc in enumerate(batch)
        ]

        # Upsert into ChromaDB
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        progress = min(batch_end, total)
        print(f"    ✅ Stored {progress}/{total} chunks ({progress * 100 // total}%)")

    print(f"\n  🗄 ChromaDB collection '{CHROMA_COLLECTION_NAME}' now has {collection.count()} documents")


# ── Main Pipeline ─────────────────────────────────────────────────────────────


def run_ingestion(reindex: bool = False, skip_scrape: bool = False) -> None:
    """
    Run the full ingestion pipeline.

    Uses the comprehensive syllabus knowledge base as the PRIMARY source,
    supplemented by any PPT files in the data directory.

    Args:
        reindex: If True, clear vector store and reprocess all files.
        skip_scrape: If True, skip the web scraping step (use existing files).
    """
    from generate_syllabus_kb import generate_documents as generate_syllabus_docs

    start_time = time.time()

    print("=" * 70)
    print("🚀 SRM Syllabus Ingestion Pipeline (Syllabus-Aware Mode)")
    print("=" * 70)

    # ── Step 0: Handle reindex ────────────────────────────────────────────
    if reindex:
        print("\n🔄 REINDEX mode: Clearing existing vector store...")
        if os.path.exists(CHROMA_PERSIST_DIR):
            shutil.rmtree(CHROMA_PERSIST_DIR)
            print("  ✅ Vector store cleared.")

    # ── Step 1: Generate syllabus KB documents ────────────────────────────
    print("\n📚 Step 1: Generating syllabus knowledge base...")
    syllabus_docs = generate_syllabus_docs()
    print(f"  ✅ Generated {len(syllabus_docs)} syllabus topic documents")

    all_chunks = list(syllabus_docs)  # Each KB doc is already chunk-sized

    # ── Step 2: Optionally load PPT files as supplementary content ────────
    print("\n📂 Step 2: Checking for supplementary PPT files...")
    os.makedirs(DATA_DIR, exist_ok=True)
    ppt_files = discover_ppt_files(DATA_DIR)

    if ppt_files:
        print(f"  📁 Found {len(ppt_files)} supplementary PPT files")

        if not skip_scrape:
            try:
                scrape_and_download(download=True)
            except Exception as e:
                print(f"  ⚠ Scraping encountered errors: {e}")

        manifest_data = load_manifest()
        documents = load_and_tag_documents(ppt_files, manifest_data)

        if documents:
            print(f"  📄 Loaded {len(documents)} PPT elements")
            ppt_chunks = chunk_documents(documents)
            all_chunks.extend(ppt_chunks)
            print(f"  ✅ Added {len(ppt_chunks)} PPT chunks")
    else:
        print("  ℹ No supplementary PPT files found (using syllabus KB only)")

    # ── Step 3: Embed and store ───────────────────────────────────────────
    print(f"\n🧠 Step 3: Embedding and storing {len(all_chunks)} chunks in ChromaDB...")
    embeddings_model = create_embeddings_model()
    store_in_chromadb(all_chunks, embeddings_model)

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"✅ Ingestion complete in {elapsed:.1f}s")
    print(f"   Syllabus KB docs: {len(syllabus_docs)}")
    print(f"   PPT chunks: {len(all_chunks) - len(syllabus_docs)}")
    print(f"   Total chunks stored: {len(all_chunks)}")
    print("=" * 70)


# ── CLI ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="SRM Syllabus Ingestion Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ingest.py                  # Normal run
  python ingest.py --reindex        # Force full reprocessing
  python ingest.py --skip-scrape    # Skip web scraping, use existing files
  python ingest.py --reindex --skip-scrape  # Rebuild from existing files
        """,
    )
    parser.add_argument(
        "--reindex",
        action="store_true",
        help="Force reprocessing of all files (clears and rebuilds vector store)",
    )
    parser.add_argument(
        "--skip-scrape",
        action="store_true",
        help="Skip web scraping, use existing files in data/ directory",
    )

    args = parser.parse_args()
    run_ingestion(reindex=args.reindex, skip_scrape=args.skip_scrape)


if __name__ == "__main__":
    main()
