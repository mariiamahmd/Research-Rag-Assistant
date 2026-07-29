from sentence_transformers import SentenceTransformer

print("Loading embedding model...")
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
print("✓ Embedding model loaded successfully.")


def embed_documents(texts):
    """
    Embed a list of document chunks.
    """
    return model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )


def embed_query(query):
    """
    Embed a user query.
    """
    return model.encode(
        query,
        normalize_embeddings=True
    )