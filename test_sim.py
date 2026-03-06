import os
import sys
from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME, EMBEDDING_MODEL, OLLAMA_BASE_URL
from langchain_community.embeddings import OllamaEmbeddings
import chromadb

query = sys.argv[1]

# Initialize embeddings
embeddings = OllamaEmbeddings(
    model=EMBEDDING_MODEL,
    base_url=OLLAMA_BASE_URL,
)

# Initialize ChromaDB
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
collection = client.get_collection(name=CHROMA_COLLECTION_NAME)

query_embedding = embeddings.embed_query(query)

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=10,
    include=["documents", "metadatas", "distances"],
)

if not results.get("documents"):
    print("No results found.")
    exit(0)

documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]

print(f"\n--- Top 10 Results for query: '{query}' ---\n")
for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
    similarity = 1.0 - dist
    subject = meta.get("subject", "Unknown")
    unit = meta.get("unit_name", "Unknown")
    print(f"{i+1}. Similarity: {similarity:.4f} | Subject: {subject} | Unit: {unit}")
