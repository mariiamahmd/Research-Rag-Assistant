from sentence_transformers import CrossEncoder

# Load the reranker model once
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

print("Reranker loaded.")
    

def rerank(question, retrieved_docs, top_k=5):
    """
    Rerank retrieved documents using a CrossEncoder.
    """

    pairs = [(question, doc["text"]) for doc in retrieved_docs]
  # Score each pair 
    scores = model.predict(pairs)
  # Add scores to docs
    for doc, score in zip(retrieved_docs, scores):
        doc["rerank_score"] = float(score)
  # Sort by rerank score (best first)
    retrieved_docs.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )
 # Return top 5
    return retrieved_docs[:top_k]