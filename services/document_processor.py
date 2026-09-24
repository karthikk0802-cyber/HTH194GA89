import pymupdf as fitz  # Updated from deprecated 'fitz' to 'pymupdf'
import docx
import io
import re

def extract_text(file_bytes, filename):
    """Extract text from PDF, DOCX, or TXT."""
    text = ""
    if filename.endswith(".pdf"):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text() + "\n"
    elif filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif filename.endswith(".txt"):
        text = file_bytes.decode("utf-8")
    return text

def chunk_text(text, chunk_size=1000, overlap=200):
    """Naive overlapping chunker. Preserves paragraphs where possible."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            # simplistic overlap
            current_chunk = current_chunk[-overlap:] + " " + para
        else:
            current_chunk += para + "\n\n"
            
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    return chunks

def extract_metadata_from_text(text, default_role="all"):
    """Naive metadata extraction from synthetic files"""
    role = default_role
    title = "Unknown Document"
    
    role_match = re.search(r"Role:\s*([a-zA-Z,]+)", text, re.IGNORECASE)
    if role_match:
        role = role_match.group(1).strip()
        
    title_match = re.search(r"Title:\s*(.+)", text, re.IGNORECASE)
    if title_match:
        title = title_match.group(1).strip()
        
    return {"title": title, "role": role}
