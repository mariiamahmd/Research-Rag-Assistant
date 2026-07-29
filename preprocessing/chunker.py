from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_document(title, filename, text):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    split_text = splitter.split_text(text)

    chunks = []

    for i, chunk in enumerate(split_text):
        chunks.append({
            "paper": title,
            "filename": filename,
            "chunk_id": i,
            "text": chunk
        })

    return chunks