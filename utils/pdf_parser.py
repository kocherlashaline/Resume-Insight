import pdfplumber
import io

def extract_text_from_pdf(uploaded_file) -> str:
    """Extract clean text from an uploaded PDF file."""
    text = []
    with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
    return "\n".join(text).strip()
