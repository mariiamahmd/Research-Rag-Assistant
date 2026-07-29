import re
import fitz


def extract_text_from_pdf(pdf_path):

    document = fitz.open(pdf_path)

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    # -------- Clean the extracted text --------

    # Remove email addresses
    text = re.sub(r"\S+@\S+", "", text)

    # Remove standalone page numbers
    text = re.sub(r"\n\s*\d+\s*\n", "\n", text)

    # Replace multiple spaces/newlines with a single space
    text = re.sub(r"\s+", " ", text)
    # Remove URLs
    text = re.sub(r"http\S+|www\.\S+", "", text)
 
# Remove multiple blank lines
    text = re.sub(r"\n{2,}", "\n", text)

# Remove repeated spaces
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()