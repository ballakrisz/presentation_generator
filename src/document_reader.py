import fitz


def extract_document_text(pdf_path: str) -> str:
    pdf = fitz.open(pdf_path)

    full_text = []

    for page in pdf:
        text = page.get_text()

        if text:
            full_text.append(text)

    return "\n".join(full_text)