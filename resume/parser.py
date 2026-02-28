from pypdf import PdfReader
from docx import Document

def parse_resume(file_path: str):

    if file_path.endswith(".pdf"):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    else:
        raise ValueError("Unsupported file format")