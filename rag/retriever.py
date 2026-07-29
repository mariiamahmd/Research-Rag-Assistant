from rag.embed import embed_query
from rag.vectorstore import search


def retrieve(question, filenames=None, top_k=5):
    """Retrieve relevant documents from selected papers"""
    
    query_embedding = embed_query(question)
    
    if query_embedding is None or len(query_embedding) == 0:
        raise Exception("Failed to generate query embedding")

    # Search across all selected files
    results = search(
        query_embedding,
        limit=top_k,
        filenames=filenames  # Can be None (search all) or list of filenames
    )

    documents = []

    for result in results:
        doc = {
            "score": result.score,
            "paper": result.payload.get("paper", "Unknown"),
            "filename": result.payload.get("filename", "Unknown"),
            "chunk_id": result.payload.get("chunk_id", 0),
            "text": result.payload.get("text", "")
        }
        
        if doc["text"].strip():
            documents.append(doc)

    return documents