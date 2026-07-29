from pathlib import Path

from rag.pipeline import add_pdf, ask

add_pdf(
    Path("data/papers/GraphRAG.pdf")
)

answer, sources = ask(
    "What is GraphRAG?"
)

print(answer)