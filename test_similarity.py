import sys
from retriever import Retriever

r = Retriever()
queries = [
    "what is inheritance?",
    "explain Laplace transforms",
    "tell me about sorting algorithms",
    "how to make a cake", # Completely off-topic
]

print("--- Similarity Test ---")
for q in queries:
    print(f"\nQuery: '{q}'")
    res = r.retrieve(q, top_k=5, threshold=0.0) # No threshold to see all scores
    if res.chunks:
        for i, c in enumerate(res.chunks[:3]):
            print(f"  {i+1}. Score: {c.similarity_score:.4f} | Subj: {c.metadata.get('subject', 'N/A')} | Unit: {c.metadata.get('unit_name', 'N/A')}")
    else:
        print("  No chunks returned.")
