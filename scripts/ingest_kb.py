import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.db import get_db, DocumentModel
from services.document_processor import extract_text, chunk_text, extract_metadata_from_text
from services.embedding import add_chunks_to_chroma, reset_collection


def ingest_all():
    db = next(get_db())
    kb_dir = "knowledge_base"
    
    if not os.path.exists(kb_dir):
        print(f"Directory {kb_dir} not found.")
        return
    
    print("Clearing old records from SQLite DocumentModel and resetting ChromaDB...")
    db.query(DocumentModel).delete()
    db.commit()
    reset_collection()

    files_to_ingest = [f for f in os.listdir(kb_dir) if f.endswith(".pdf") or f.endswith(".txt")]
    # Prioritize PDFs, if both exist prefer PDF
    processed_bases = set()
    
    for filename in sorted(files_to_ingest):
        base_name, ext = os.path.splitext(filename)
        # If PDF exists and processed, don't duplicate with TXT unless desired
        if ext == ".txt" and f"{base_name}.pdf" in files_to_ingest:
            continue
            
        filepath = os.path.join(kb_dir, filename)
        with open(filepath, "rb") as f:
            file_bytes = f.read()
            
        text = extract_text(file_bytes, filename)
        meta = extract_metadata_from_text(text)
        
        # If title wasn't extracted from header regex, format nicely from filename
        if meta["title"] == "Unknown Document":
            meta["title"] = base_name.replace("_", " ")
            
        chunks = chunk_text(text, chunk_size=800, overlap=150)
        if not chunks:
            continue
        
        # Save to DB
        new_doc = DocumentModel(
            filename=filename,
            title=meta["title"],
            role=(meta["role"] or "all").lower(),
            chunk_count=len(chunks)
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        
        # Save to Chroma
        ids = [f"doc_{new_doc.id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{"doc_id": str(new_doc.id), "title": meta["title"], "role": (meta["role"] or "all").lower(), "filename": filename} for _ in chunks]
        add_chunks_to_chroma(chunks, metadatas, ids)
        print(f"Ingested {filename} (Title: '{meta['title']}', Role: '{meta['role']}') - {len(chunks)} chunks.")

if __name__ == "__main__":
    ingest_all()
    print("Done ingesting knowledge base.")
