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
from rag.llm import answer, compare_answers


def add_pdf(pdf_path):
    """Add PDF to RAG system - Qdrant is source of truth"""
    
    print("Adding:", pdf_path)

    filename = Path(pdf_path).name
 # Check if already loaded
    if paper_exists(filename):
        print("Already loaded in Qdrant.")
        return
   # Extract and chunk
    chunks = process_pdf(pdf_path)
    print("Chunks:", len(chunks))


    texts = [chunk["text"] for chunk in chunks]
  # Embed chunks
    embeddings = embed_documents(texts)


 # Create collection if first paper
    print("Creating collection...")
    create_collection(len(embeddings[0]))

  # Upload to Qdrant
    print("Uploading...")
    upload_chunks(chunks, embeddings)

    # Verify upload
    if paper_exists(filename):
        print("Upload verified - file is in Qdrant ✓")
    else:
        print("ERROR: Upload failed - file not found in Qdrant ✗")


def ask(question, filenames=None, compare=False):

    # Check if any papers are loaded
    if not collection_exists():
        raise Exception("No papers indexed. Upload a paper first.")

 # Retrieve top 20 similar chunks
    docs = retrieve(
        question,
        filenames=filenames,
        top_k=20,
    )



    
  # Rerank to top 5
    best = rerank(question, docs, top_k=8)

    if not best:
      return "I couldn't find the answer in the uploaded papers.", []

    THRESHOLD = -3.0

    if best[0]["rerank_score"] < THRESHOLD:
        return "I couldn't find the answer in the uploaded papers.", []

    # -------------------------
    # Compare Mode
    # -------------------------
    if compare:

        if filenames is None or len(filenames) != 2:
            return (
                "Please select exactly two papers for comparison.",
                []
            )

        paper1, paper2 = filenames

        docs1 = [d for d in best if d["filename"] == paper1]
        docs2 = [d for d in best if d["filename"] == paper2]

        if not docs1 or not docs2:
            return (
                "Couldn't retrieve enough information from both papers.",
                best,
            )

        return compare_answers(
            question,
            docs1,
            docs2,
        ), best

    # -------------------------
    # Normal Mode
    # -------------------------
    return answer(question, best), best