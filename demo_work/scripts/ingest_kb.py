import os
from services.db import get_db, DocumentModel
from services.document_processor import extract_text, chunk_text, extract_metadata_from_text
from services.embedding import add_chunks_to_chroma

def ingest_all():
    db = next(get_db())
    kb_dir = "knowledge_base"
    
    if not os.path.exists(kb_dir):
        print(f"Directory {kb_dir} not found.")
        return
        
    for filename in os.listdir(kb_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(kb_dir, filename)
            with open(filepath, "rb") as f:
                file_bytes = f.read()
                
            text = extract_text(file_bytes, filename)
            meta = extract_metadata_from_text(text)
            chunks = chunk_text(text)
            
            # Save to DB
            new_doc = DocumentModel(
                filename=filename,
                title=meta["title"],
                role=meta["role"],
                chunk_count=len(chunks)
            )
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)
            
            # Save to Chroma
            ids = [f"doc_{new_doc.id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{"doc_id": str(new_doc.id), "title": meta["title"], "role": meta["role"]} for _ in chunks]
            add_chunks_to_chroma(chunks, metadatas, ids)
            print(f"Ingested {filename} - {len(chunks)} chunks.")

if __name__ == "__main__":
    ingest_all()
    print("Done ingesting knowledge base.")
