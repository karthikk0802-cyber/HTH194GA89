import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function AdminCenter() {
  const [docs, setDocs] = useState([]);
  const [feedbackList, setFeedbackList] = useState([]);
  const [loading, setLoading] = useState(true);

  const [uploadFile, setUploadFile] = useState(null);
  const [uploadOwner, setUploadOwner] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      api.getDocuments(),
      api.getFeedbackList()
    ])
      .then(([docData, fbData]) => {
        setDocs(docData);
        setFeedbackList(fbData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  const handleToggleDoc = async (docId) => {
    try {
      await api.toggleDocument(docId);
      fetchData();
    } catch (err) {
      alert('Error toggling document status: ' + err.message);
    }
  };

  const handleDeleteDoc = async (docId) => {
    if (!window.confirm('Delete this document from SQLite and ChromaDB?')) return;
    try {
      await api.deleteDocument(docId);
      fetchData();
    } catch (err) {
      alert('Error deleting document: ' + err.message);
    }
  };

  const handleApproveDoc = async (docId) => {
    try {
      await api.approveDocument(docId);
      fetchData();
    } catch (err) {
      alert('Error approving document: ' + err.message);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploading(true);
    setUploadSuccess('');
    try {
      const res = await api.uploadDocument(uploadFile, uploadOwner);
      setUploadSuccess(`“${res.document.title}” staged as draft (${res.document.chunk_count} chunks). Approve to activate in RAG.`);
      setUploadFile(null);
      setUploadOwner('');
      fetchData();
    } catch (err) {
      alert('Upload failed: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return <span className="spinner spinner-lg" />;
  }

  const activeDocsCount = docs.filter(d => d.status === 'active').length;

  return (
    <div>
      <div className="page-header">
        <h1><span className="kicker">01</span>Knowledge admin</h1>
        <p>Policy documents, retrieval lifecycle, and learner feedback.</p>
      </div>

      <div className="section">
        <div className="row" style={{ gap: 48 }}>
          <div>
            <div className="kpi-label">Documents</div>
            <div className="kpi">{docs.length}</div>
          </div>
          <div>
            <div className="kpi-label">Active in RAG</div>
            <div className="kpi">{activeDocsCount}</div>
          </div>
          <div>
            <div className="kpi-label">Flagged items</div>
            <div className="kpi">{feedbackList.length}</div>
          </div>
        </div>
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">02</span>Ingest document</h3>
          <span className="note">lands as draft</span>
        </div>
        <form onSubmit={handleUploadSubmit} className="row">
          <input type="file" accept=".txt,.pdf,.docx" onChange={(e) => setUploadFile(e.target.files[0])} />
          <input
            type="text"
            className="form-input"
            style={{ maxWidth: 220 }}
            placeholder="Owning team"
            value={uploadOwner}
            onChange={(e) => setUploadOwner(e.target.value)}
          />
          <button type="submit" className="btn btn-primary" disabled={uploading || !uploadFile}>
            {uploading ? <span className="spinner" /> : 'Chunk & stage'}
          </button>
        </form>
        {uploadSuccess && <div className="notice notice-ok mt">{uploadSuccess}</div>}
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">03</span>Documents</h3>
        </div>
        <div className="custom-table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Scope</th>
                <th>Chunks</th>
                <th>Status</th>
                <th>Owner / Ver</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {docs.map(doc => (
                <tr key={doc.id}>
                  <td>
                    <strong>#{doc.id} — {doc.title}</strong>
                    <div className="cell-sub">{doc.filename}</div>
                  </td>
                  <td><span className="badge badge-indigo">{doc.role}</span></td>
                  <td>{doc.chunk_count}</td>
                  <td>
                    <span className={`badge ${doc.status === 'active' ? 'badge-emerald' : doc.status === 'draft' ? 'badge-amber' : 'badge-gray'}`}>
                      {doc.status}
                    </span>
                    {doc.review_after && <div className="cell-sub">review {doc.review_after.split('T')[0]}</div>}
                  </td>
                  <td>
                    <div>{doc.owner || '—'}</div>
                    <div className="cell-sub">v{doc.version || 1}</div>
                  </td>
                  <td>
                    <div className="row">
                      {doc.status === 'draft' && (
                        <button className="btn btn-sm btn-primary" onClick={() => handleApproveDoc(doc.id)}>Approve</button>
                      )}
                      <button className="btn btn-sm btn-secondary" onClick={() => handleToggleDoc(doc.id)}>
                        {doc.status === 'active' ? 'Disable' : 'Enable'}
                      </button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDeleteDoc(doc.id)}>Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">04</span>Learner feedback</h3>
        </div>
        {feedbackList.length > 0 ? (
          <div>
            {feedbackList.map(fb => (
              <div key={fb.id} className="dir-row">
                <div>
                  <div>
                    <div className="dir-main">{fb.question_text}</div>
                    <div className="dir-sub">{fb.submitted_at?.split('T')[0]} · {fb.feedback_text || 'No comment'}</div>
                  </div>
                  <span className="badge badge-amber">{fb.reason}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="sub">No flags submitted yet.</p>
        )}
      </div>
    </div>
  );
}
