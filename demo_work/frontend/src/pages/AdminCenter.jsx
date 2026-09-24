import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function AdminCenter() {
  const [docs, setDocs] = useState([]);
  const [feedbackList, setFeedbackList] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Upload state
  const [uploadFile, setUploadFile] = useState(null);
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
    if (!window.confirm('Are you sure you want to delete this document from SQLite and ChromaDB?')) return;
    try {
      await api.deleteDocument(docId);
      fetchData();
    } catch (err) {
      alert('Error deleting document: ' + err.message);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploading(true);
    setUploadSuccess('');
    try {
      const res = await api.uploadDocument(uploadFile);
      setUploadSuccess(`Successfully ingested '${res.document.title}' (${res.document.chunk_count} chunks embedded into ChromaDB).`);
      setUploadFile(null);
      fetchData();
    } catch (err) {
      alert('Upload failed: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <div className="spinner" style={{ width: '36px', height: '36px' }}></div>
      </div>
    );
  }

  const activeDocsCount = docs.filter(d => d.status === 'active').length;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Knowledge Administration & Governance</h1>
          <p>Manage corporate policy documents, vector embedding lifecycle, and learner audit feedback.</p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid-3" style={{ marginBottom: '28px' }}>
        <div className="glass-card">
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>INDEXED DOCUMENTS</span>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#ffffff', marginTop: '4px' }}>
            {docs.length}
          </div>
        </div>

        <div className="glass-card">
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>ACTIVE IN RAG</span>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#34d399', marginTop: '4px' }}>
            {activeDocsCount}
          </div>
        </div>

        <div className="glass-card">
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>FLAGGED QUIZ ITEMS</span>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#f59e0b', marginTop: '4px' }}>
            {feedbackList.length}
          </div>
        </div>
      </div>

      {/* Document Upload Card */}
      <div className="glass-card" style={{ marginBottom: '28px' }}>
        <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Ingest New Knowledge Base Document</h3>
        <form onSubmit={handleUploadSubmit} style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            type="file"
            accept=".txt,.pdf,.docx"
            onChange={(e) => setUploadFile(e.target.files[0])}
            style={{
              padding: '10px',
              background: 'rgba(15, 23, 42, 0.7)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text-primary)',
              flex: 1,
              minWidth: '260px'
            }}
          />
          <button
            type="submit"
            className="btn btn-primary"
            style={{ padding: '12px 28px' }}
            disabled={uploading || !uploadFile}
          >
            {uploading ? <div className="spinner"></div> : '📤 Extract, Chunk & Index into ChromaDB'}
          </button>
        </form>

        {uploadSuccess && (
          <div style={{ marginTop: '14px', color: '#6ee7b7', fontSize: '14px', background: 'rgba(16, 185, 129, 0.1)', padding: '10px 14px', borderRadius: '8px' }}>
            ✓ {uploadSuccess}
          </div>
        )}
      </div>

      {/* Documents Table */}
      <div className="glass-card" style={{ marginBottom: '28px' }}>
        <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Indexed Knowledge Base Documents</h3>
        <div className="custom-table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Document Title</th>
                <th>Role Scope</th>
                <th>Embedded Chunks</th>
                <th>RAG Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {docs.map(doc => (
                <tr key={doc.id}>
                  <td>#{doc.id}</td>
                  <td>
                    <strong>{doc.title}</strong>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{doc.filename}</div>
                  </td>
                  <td>
                    <span className="badge badge-indigo">{doc.role}</span>
                  </td>
                  <td>{doc.chunk_count} chunks</td>
                  <td>
                    <span className={`badge ${doc.status === 'active' ? 'badge-emerald' : 'badge-gray'}`}>
                      {doc.status}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '4px 10px', fontSize: '11px' }}
                        onClick={() => handleToggleDoc(doc.id)}
                      >
                        {doc.status === 'active' ? 'Disable' : 'Enable'}
                      </button>
                      <button
                        className="btn btn-danger"
                        style={{ padding: '4px 10px', fontSize: '11px' }}
                        onClick={() => handleDeleteDoc(doc.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quiz Feedback Table */}
      <div className="glass-card">
        <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Learner Quiz Feedback & Audit Log</h3>
        {feedbackList.length > 0 ? (
          <div className="custom-table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Question Prompt</th>
                  <th>Reported Reason</th>
                  <th>Learner Comments</th>
                </tr>
              </thead>
              <tbody>
                {feedbackList.map(fb => (
                  <tr key={fb.id}>
                    <td style={{ whiteSpace: 'nowrap', fontSize: '12px', color: 'var(--text-muted)' }}>
                      {fb.submitted_at?.split('T')[0]}
                    </td>
                    <td style={{ maxWidth: '350px' }}>
                      <div style={{ fontSize: '13px', color: '#ffffff' }}>{fb.question_text}</div>
                    </td>
                    <td>
                      <span className="badge badge-amber">{fb.reason}</span>
                    </td>
                    <td>
                      <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                        {fb.feedback_text || 'No additional comment'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '14px' }}>
            No question flags or accuracy feedback submitted by learners yet.
          </div>
        )}
      </div>
    </div>
  );
}
