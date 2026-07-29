from sentence_transformers import CrossEncoder

# Load the reranker model once
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

print("Reranker loaded.")


def rerank(question, retrieved_docs, top_k=5):
    """
    Rerank retrieved documents using a CrossEncoder.
    """

    pairs = [(question, doc["text"]) for doc in retrieved_docs]

    scores = model.predict(pairs)

    for doc, score in zip(retrieved_docs, scores):
        doc["rerank_score"] = float(score)

    retrieved_docs.sort(
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    return retrieved_docs[:top_k]