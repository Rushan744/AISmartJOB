import PyPDF2
import io
from fastapi import HTTPException

def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    Extracts text from a PDF file provided as bytes.
    """
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")
    return text