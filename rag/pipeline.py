from pathlib import Path

from preprocessing.processor import process_pdf
from rag.vectorstore import collection_exists
from rag.embed import embed_documents
from rag.vectorstore import (
    create_collection,
    upload_chunks,
    paper_exists,
)
from rag.retriever import retrieve
from rag.reranker import rerank
from rag.llm import answer


def add_pdf(pdf_path):
    """Add PDF to RAG system - Qdrant is source of truth"""
    
    print("Adding:", pdf_path)

    filename = Path(pdf_path).name

    if paper_exists(filename):
        print("Already loaded in Qdrant.")
        return

    chunks = process_pdf(pdf_path)
    print("Chunks:", len(chunks))

    texts = [chunk["text"] for chunk in chunks]

    embeddings = embed_documents(texts)

    print("Creating collection...")
    create_collection(len(embeddings[0]))

    print("Uploading...")
    upload_chunks(chunks, embeddings)

    # Verify upload
    if paper_exists(filename):
        print("Upload verified - file is in Qdrant ✓")
    else:
        print("ERROR: Upload failed - file not found in Qdrant ✗")
def ask(question, filenames=None):

  
    if not collection_exists():
        raise Exception("No papers indexed. Upload a paper first.")

    docs = retrieve(
        question,
        filenames=filenames,
        top_k=20,
    )

    best = rerank(question, docs, top_k=5)

    if not best:
        return "I couldn't find the answer in the uploaded papers.", []



    THRESHOLD = -3.0

    if best[0]["rerank_score"] < THRESHOLD:
        return "I couldn't find the answer in the uploaded papers.", []

    return answer(question, best), best