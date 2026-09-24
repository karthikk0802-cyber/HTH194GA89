import os

CHROMA_DATA_PATH = "./chroma_db"
_collection = None

def get_collection():
    global _collection
    if _collection is None:
        import chromadb
        from chromadb.utils import embedding_functions
        client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
        bge_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-small-en-v1.5")
        _collection = client.get_or_create_collection(
            name="nexora_knowledge_base",
            embedding_function=bge_ef,
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

def add_chunks_to_chroma(chunks, metadatas, ids):
    """Add document chunks to ChromaDB."""
    col = get_collection()
    col.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )

def search_chroma(query, n_results=5, role_filter=None):
    """Search for relevant chunks."""
    col = get_collection()
    where_clause = {}
    if role_filter and role_filter != "all":
        where_clause["role"] = {"$in": ["all", role_filter]}
        
    results = col.query(
        query_texts=[query],
        n_results=n_results,
        where=where_clause if where_clause else None
    )
    return results

def delete_document_from_chroma(doc_id):
    """Remove all chunks associated with a document ID."""
    col = get_collection()
    col.delete(where={"doc_id": str(doc_id)})

def reset_collection():
    """Clear all documents from the ChromaDB collection."""
    global _collection
    import chromadb
    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    try:
        client.delete_collection("nexora_knowledge_base")
    except Exception:
        pass
    _collection = None
    return get_collection()

