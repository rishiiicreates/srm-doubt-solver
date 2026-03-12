import sys
from retriever import retrieve

queries = [
    "what is inheritance?",
    "explain Laplace transforms",
    "tell me about sorting algorithms",
    "how to make a cake", # Completely off-topic
]

print("--- Similarity Test ---")
for q in queries:
    print(f"\nQuery: '{q}'")
    # Call the singleton wrapper instead
    res = retrieve(q)
    if res.chunks:
        for i, c in enumerate(res.chunks[:3]):
            print(f"  {i+1}. Score: {c.similarity_score:.4f} | Subj: {c.subject} | Unit: {c.unit_name}")
    else:
        print("  No chunks returned.")
