import streamlit as st
import pandas as pd
from services.db import get_db, DocumentModel
from services.document_processor import extract_text, chunk_text, extract_metadata_from_text
from services.embedding import add_chunks_to_chroma, delete_document_from_chroma

st.set_page_config(page_title="Knowledge Admin", page_icon="⚙️", layout="wide")

st.title("Knowledge Base Administration")
st.markdown("Upload, index, and manage documents for the RAG pipeline.")

db = next(get_db())

# Document Upload Section
with st.expander("Upload New Document", expanded=True):
    uploaded_file = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
    if st.button("Process & Index") and uploaded_file:
        with st.spinner("Extracting text and generating embeddings..."):
            file_bytes = uploaded_file.read()
            text = extract_text(file_bytes, uploaded_file.name)
            
            meta = extract_metadata_from_text(text)
            chunks = chunk_text(text)
            
            # Save to DB
            new_doc = DocumentModel(
                filename=uploaded_file.name,
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
            
            st.success(f"Indexed '{meta['title']}' with {len(chunks)} chunks!")

# Manage Documents Section
st.subheader("Manage Documents")
docs = db.query(DocumentModel).all()

if docs:
    doc_data = [{"ID": d.id, "Title": d.title, "Role": d.role, "Status": d.status, "Chunks": d.chunk_count} for d in docs]
    st.table(pd.DataFrame(doc_data))
    
    col1, col2 = st.columns(2)
    with col1:
        doc_id_to_toggle = st.number_input("Document ID to Toggle Status", min_value=1, step=1)
        if st.button("Toggle Active/Inactive"):
            doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id_to_toggle).first()
            if doc:
                doc.status = "inactive" if doc.status == "active" else "active"
                db.commit()
                st.success(f"Toggled status of Doc {doc.id} to {doc.status}")
                st.rerun()
    with col2:
        doc_id_to_delete = st.number_input("Document ID to Delete", min_value=1, step=1)
        if st.button("Delete Document"):
            doc = db.query(DocumentModel).filter(DocumentModel.id == doc_id_to_delete).first()
            if doc:
                delete_document_from_chroma(doc.id)
                db.delete(doc)
                db.commit()
                st.success(f"Deleted Doc {doc.id}")
                st.rerun()
else:
    st.info("No documents indexed yet.")

# NEW: Admin Metrics & Feedback (Phase 10)
st.markdown("---")
st.subheader("Knowledge Health & Feedback Metrics")

from services.db import QuizFeedbackModel
feedbacks = db.query(QuizFeedbackModel).order_by(QuizFeedbackModel.submitted_at.desc()).all()

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Documents Indexed", len(docs) if docs else 0)
    active_docs = sum(1 for d in docs if d.status == "active") if docs else 0
    st.metric("Active Documents", active_docs)

with col2:
    st.metric("User Feedback Items", len(feedbacks))
    
if feedbacks:
    st.write("**Recent Quiz Feedback (Requires Review)**")
    fb_data = [{"Date": f.submitted_at.strftime("%Y-%m-%d"), "Question": f.question_text[:50]+"...", "Reason": f.reason, "Comments": f.feedback_text} for f in feedbacks]
    st.table(pd.DataFrame(fb_data))
