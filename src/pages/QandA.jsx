import React, { useState } from 'react';
import { api } from '../services/api';

export default function QandA() {
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

  return (
    <div>
      <div className="page-header">
        <h1><span className="kicker">01</span>Knowledge Coach</h1>
        <p>Answers grounded in verified Nexora policy documents, with citations.</p>
      </div>

      <div className="section">
        <div className="row">
          <input
            type="text"
            className="form-input"
            style={{ flex: 1, minWidth: 240 }}
            placeholder="Ask about policies, tools, procedures…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') handleAsk(); }}
          />
          <button className="btn btn-primary" onClick={() => handleAsk()} disabled={loading || !query.trim()}>
            {loading ? <span className="spinner" /> : 'Ask'}
          </button>
          <select className="form-select" style={{ width: 'auto' }} value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
            <option value="all">All company</option>
            <option value="engineering">Engineering</option>
            <option value="devops">DevOps</option>
            <option value="product">Product</option>
            <option value="sales">Sales</option>
          </select>
        </div>
        <div className="row mt">
          <span className="kpi-label">Try</span>
          {sampleQuestions.slice(0, 3).map((sq, i) => (
            <button key={i} type="button" className="btn btn-sm btn-secondary" onClick={() => { setQuery(sq); handleAsk(sq); }}>
              {sq}
            </button>
          ))}
        </div>
      </div>

      {response && (
        <div className="section">
          <div className="sec-head">
            <h3><span className="idx">02</span>Answer</h3>
            <span className="badge badge-gray">Confidence: {response.confidence}</span>
          </div>
          <p style={{ fontSize: '1.15rem', maxWidth: '68ch', whiteSpace: 'pre-line' }}>
            {response.answer}
          </p>

          {response.citations && response.citations.length > 0 && (
            <div className="mt">
              <span className="kpi-label">Sources</span>
              <div className="row mt">
                {response.citations.map((c, i) => (
                  <span key={i} className="badge badge-indigo">{c}</span>
                ))}
              </div>
            </div>
          )}

          <div className="mt">
            <button className="btn btn-sm btn-secondary" onClick={() => setShowDebug(!showDebug)}>
              {showDebug ? 'Hide evidence' : 'Show retrieved evidence'}
            </button>
            {showDebug && response.chunks && (
              <div className="mt">
                {response.chunks.map((chunk, i) => (
                  <div key={i} className="dir-row">
                    <div>
                      <div>
                        <div className="dir-main">{chunk.title}</div>
                        <div className="dir-sub">“{chunk.text}”</div>
                      </div>
                      <span className="badge badge-gray">d={chunk.distance?.toFixed(4) || 'n/a'}</span>
                    </div>
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
