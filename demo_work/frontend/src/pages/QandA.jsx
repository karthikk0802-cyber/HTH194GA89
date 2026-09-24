import React, { useState } from 'react';
import { api } from '../services/api';

export default function QandA({ selectedRole }) {
  const [query, setQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [showDebug, setShowDebug] = useState(false);

  const sampleQuestions = [
    'What are the core hours and remote work stipends?',
    'What is our Git branching strategy and PR approval rules?',
    'When do deployments happen and what are the restrictions?',
    'How often is password rotation and security training conducted?',
    'What is our expense per diem and submission process?'
  ];

  const handleAsk = async (qToAsk) => {
    const activeQuery = qToAsk || query;
    if (!activeQuery.trim()) return;

    setLoading(true);
    try {
      const res = await api.askQA(activeQuery, roleFilter);
      setResponse(res);
    } catch (err) {
      alert('Error searching knowledge base: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceBadge = (conf) => {
    switch (conf) {
      case 'Strong':
        return <span className="badge badge-emerald">Evidence Confidence: Strong</span>;
      case 'Moderate':
        return <span className="badge badge-indigo">Evidence Confidence: Moderate</span>;
      case 'Limited':
        return <span className="badge badge-amber">Evidence Confidence: Limited</span>;
      default:
        return <span className="badge badge-rose">Evidence Confidence: Insufficient</span>;
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>AI Knowledge Coach</h1>
          <p>Grounded Retrieval-Augmented Generation (RAG) powered by Mistral AI + ChromaDB vector embeddings.</p>
        </div>
      </div>

      {/* Query Card */}
      <div className="glass-card" style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
          <input
            type="text"
            className="form-input"
            style={{ fontSize: '15px', padding: '14px 18px' }}
            placeholder="Ask anything about Nexora policies, tools, or procedures (e.g. 'What is the internet stipend?')"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleAsk(); }}
          />
          <button
            className="btn btn-primary"
            style={{ padding: '0 28px', fontSize: '15px', flexShrink: 0 }}
            onClick={() => handleAsk()}
            disabled={loading || !query.trim()}
          >
            {loading ? <div className="spinner"></div> : 'Consult Coach'}
          </button>
        </div>

        {/* Filters & Suggestions */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>POPULAR INQUIRIES:</span>
            {sampleQuestions.slice(0, 3).map((sq, i) => (
              <button
                key={i}
                type="button"
                className="btn btn-secondary"
                style={{ padding: '4px 10px', fontSize: '12px' }}
                onClick={() => { setQuery(sq); handleAsk(sq); }}
              >
                {sq}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>FILTER ROLE:</span>
            <select
              className="form-select"
              style={{ width: 'auto', padding: '6px 12px', fontSize: '12px' }}
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
            >
              <option value="all">All Company</option>
              <option value="engineering">Engineering</option>
              <option value="devops">DevOps</option>
              <option value="product">Product</option>
              <option value="sales">Sales</option>
            </select>
          </div>
        </div>
      </div>

      {/* Answer View */}
      {response && (
        <div className="glass-card" style={{ marginBottom: '28px', borderLeft: '4px solid var(--primary)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '20px' }}>🤖</span>
              <h3 style={{ fontSize: '18px' }}>Grounded AI Response</h3>
            </div>
            {getConfidenceBadge(response.confidence)}
          </div>

          <div style={{
            fontSize: '15px',
            lineHeight: 1.7,
            color: '#f9fafb',
            background: 'rgba(255, 255, 255, 0.02)',
            padding: '20px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-subtle)',
            marginBottom: '20px',
            whiteSpace: 'pre-line'
          }}>
            {response.answer}
          </div>

          {/* Citations */}
          {response.citations && response.citations.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', display: 'block', marginBottom: '8px' }}>
                Verified Policy Citations:
              </span>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {response.citations.map((c, i) => (
                  <span key={i} className="badge badge-indigo" style={{ padding: '6px 12px', fontSize: '13px' }}>
                    📄 {c}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Debug & Transparency Toggle */}
          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)' }}>
            <button
              className="btn btn-secondary"
              style={{ padding: '6px 12px', fontSize: '12px' }}
              onClick={() => setShowDebug(!showDebug)}
            >
              {showDebug ? 'Hide RAG Evidence Chunks ▲' : 'View Auditable RAG Evidence & Distances ▼'}
            </button>

            {showDebug && response.chunks && (
              <div style={{ marginTop: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)' }}>
                  Retrieved from ChromaDB Vector Store ({response.chunks.length} chunks):
                </span>
                {response.chunks.map((chunk, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '12px 16px',
                      background: 'rgba(15, 23, 42, 0.8)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-md)',
                      fontSize: '13px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <strong style={{ color: '#a5b4fc' }}>{chunk.title}</strong>
                      <span className="badge badge-gray" style={{ fontSize: '11px' }}>
                        Cosine Distance: {chunk.distance?.toFixed(4) || 'N/A'}
                      </span>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                      "{chunk.text}"
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
