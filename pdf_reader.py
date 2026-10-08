from pypdf import PdfReader


def read_pdf_text(path):
    """Open a PDF and return all its text as one string."""
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


if __name__ == "__main__":
    print(read_pdf_text("sample_datasheet.pdf"))