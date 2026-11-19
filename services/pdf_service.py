"""
PDF Extraction and Validation Service.
"""
import os
from pypdf import PdfReader
from pypdf import errors as pypdf_errors
from config import (
    logger,
    MAX_PDF_SIZE_BYTES,
    MAX_PDF_PAGES,
    MIN_EXTRACTED_CHARS,
)

def extract_text_from_pdf(pdf_file) -> str:
    """
    Safely extract plain text from an uploaded PDF file with security limits:
    - Rejects files exceeding MAX_PDF_SIZE_BYTES (10 MB)
    - Rejects files exceeding MAX_PDF_PAGES (10 pages)
    - Detects image-only / scanned documents (<50 characters)
    - Catches specific pypdf exceptions with server-side logging
    """
    if pdf_file is None:
        return ""
    
    file_path = None
    if isinstance(pdf_file, str):
        file_path = pdf_file
    elif hasattr(pdf_file, "name"):
        file_path = pdf_file.name
    elif isinstance(pdf_file, dict) and "name" in pdf_file:
        file_path = pdf_file["name"]
        
    if not file_path or not os.path.exists(file_path):
        return ""

    # Check file size limit (Item 9)
    try:
        file_size = os.path.getsize(file_path)
        if file_size > MAX_PDF_SIZE_BYTES:
            size_mb = file_size / (1024 * 1024)
            logger.warning("PDF upload rejected: file size %.2f MB exceeds 10 MB limit", size_mb)
            return f"Error reading PDF: File size ({size_mb:.1f} MB) exceeds maximum allowed limit of 10 MB. Please upload a smaller PDF."
    except OSError as e:
        logger.error("Failed to inspect PDF size for '%s': %s", file_path, e, exc_info=True)
        return "Error reading PDF: The uploaded file could not be accessed."
        
    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        # Check page count limit (Item 9)
        if total_pages > MAX_PDF_PAGES:
            logger.warning("PDF upload rejected: %d pages exceeds limit of %d", total_pages, MAX_PDF_PAGES)
            return f"Error reading PDF: File has {total_pages} pages, exceeding the 10-page limit. Please upload a resume under 10 pages."

        text_parts = []
        for idx, page in enumerate(reader.pages):
            extracted = page.extract_text()
            if extracted:
                text_parts.append(extracted)
        full_text = "\n".join(text_parts).strip()

        # Scanned / Image-only PDF detection (Item 10)
        if len(full_text) < MIN_EXTRACTED_CHARS:
            logger.warning("PDF '%s' extracted only %d characters; suspected scanned/image document.", file_path, len(full_text))
            return "Error reading PDF: This PDF appears to be a scanned image or contains no selectable text. Please upload a text-based PDF or use OCR first."

        return full_text

    except (pypdf_errors.PdfReadError, pypdf_errors.PyPdfError) as e:
        logger.error("PDF read error for file '%s': %s", file_path, e, exc_info=True)
        return "Error reading PDF: The file appears to be corrupted, password-protected, or unreadable."
    except (FileNotFoundError, PermissionError) as e:
        logger.error("File access error for PDF '%s': %s", file_path, e, exc_info=True)
        return "Error reading PDF: The uploaded file could not be accessed."
    except Exception as e:
        logger.error("Unexpected error reading PDF '%s': %s", file_path, e, exc_info=True)
        return "Error reading PDF: An unexpected error occurred while extracting text."
