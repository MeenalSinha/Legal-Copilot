"""
Document Processing Service
Handles PDF parsing and text extraction
"""

import io
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return "\n\n".join(pages)
    except ImportError:
        logger.warning("pdfplumber not available, trying PyPDF2")

    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise ValueError(f"Could not extract text from PDF: {e}")


def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Remove excessive whitespace
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'\t', ' ', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    # Remove page numbers and headers
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)

    # Remove very short lines (likely artifacts)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if len(stripped) > 2 or stripped == '':
            cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)

    return text.strip()


def validate_document(text: str) -> Optional[str]:
    """Validate that the document is a valid T&C or privacy policy."""
    if len(text.strip()) < 100:
        return "Document is too short to analyze."

    if len(text) > 500000:
        return "Document exceeds maximum size (500,000 characters)."

    return None
