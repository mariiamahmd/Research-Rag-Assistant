from pathlib import Path

from preprocessing.pdf_loader import extract_text_from_pdf
from preprocessing.chunker import chunk_document

# loading the pdf and prepare it for embedding
def process_pdf(pdf_path):
    pdf_path = Path(pdf_path)

    text = extract_text_from_pdf(pdf_path)

    chunks = chunk_document(
        title=pdf_path.stem,
        filename=pdf_path.name,
        text=text
    )

    return chunks