from sentence_transformers import SentenceTransformer

print("Loading embedding model...")
model = SentenceTransformer("BAAI/bge-small-en-v1.5") # vetor of 384 dim
print("✓ Embedding model loaded successfully.")

# embedding of the chunks
def embed_documents(texts):
    """
    Embed a list of document chunks.
    """
    return model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True
    )

# embedding of the question
def embed_query(query):
    """
    Embed a user query.
    """
    return model.encode(
        query,
        normalize_embeddings=True
    )