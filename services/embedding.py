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
    """Search for relevant chunks. Draft/inactive docs are never returned.

    Filtering is client-side so legacy chunks without a status key keep
    working (missing status == active). Callers and return shape unchanged.
    """
    col = get_collection()
    where_clause = {}
    if role_filter and role_filter != "all":
        where_clause["role"] = {"$in": ["all", role_filter]}

    fetch_n = min(n_results * 3, 30)
    results = col.query(
        query_texts=[query],
        n_results=fetch_n,
        where=where_clause if where_clause else None
    )
    docs = (results.get("documents") or [[]])[0]
    metas = (results.get("metadatas") or [[]])[0]
    ids = (results.get("ids") or [[]])[0]
    dists = (results.get("distances") or [[]])[0]
    kept_docs, kept_metas, kept_ids, kept_dists = [], [], [], []
    for i, (doc, meta) in enumerate(zip(docs, metas)):
        status = (meta or {}).get("status", "active")
        if status in ("draft", "inactive"):
            continue
        kept_docs.append(doc)
        kept_metas.append(meta)
        if i < len(ids):
            kept_ids.append(ids[i])
        if i < len(dists):
            kept_dists.append(dists[i])
        if len(kept_docs) >= n_results:
            break
    results["documents"] = [kept_docs]
    results["metadatas"] = [kept_metas]
    if "ids" in results:
        results["ids"] = [kept_ids]
    if "distances" in results:
        results["distances"] = [kept_dists]
    return results


def set_document_status(doc_id, chunk_count, status, base_metadata=None):
    """Tag all chunks of a doc with a lifecycle status (active/draft/inactive)."""
    col = get_collection()
    base = dict(base_metadata or {})
    base["doc_id"] = str(doc_id)
    base["status"] = status
    ids = [f"doc_{doc_id}_chunk_{i}" for i in range(chunk_count or 0)]
    if not ids:
        return
    col.update(ids=ids, metadatas=[dict(base) for _ in ids])

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

