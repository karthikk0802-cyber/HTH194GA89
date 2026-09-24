import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

// V2 baseline: per-topic general questions for the role card, then strength profile.
// Submit path reuses v1-calculated scores (score_baseline wraps evaluate_diagnostic),
// and XP is awarded by the existing backend flow via submitBaseline mirror.
export default function PreAssessmentV2({ selectedRole, setActiveTab }) {
  const { user } = useAuth();
  const [perTopic, setPerTopic] = useState(3);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  const load = () => {
    setLoading(true);
    setResult(null);
    setAnswers({});
    api.getBaselineQuestions(selectedRole, perTopic, user?.username || '')
      .then((qData) => setQuestions(qData || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [selectedRole, perTopic]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await api.submitBaseline(user?.username || 'demo_user', selectedRole, answers);
      setResult(res);
    } catch (err) {
      alert('Baseline evaluation failed: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Baseline Assessment v2 — {selectedRole}</h1>
          <p>General questions per required topic. Strengths bypass, weaknesses get personalized deep dives.</p>
        </div>
      </div>
      <div className="glass-card" style={{ marginBottom: 20, display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
        <label style={{ fontSize: 12, color: 'var(--text-muted)' }}>ROLE CARD (assigned by admin)</label>
        <span className="badge badge-indigo">{selectedRole}</span>
        <label style={{ fontSize: 12, color: 'var(--text-muted)' }}>PER TOPIC</label>
        <select className="form-select" style={{ width: 'auto' }} value={perTopic} onChange={(e) => setPerTopic(Number(e.target.value))}>
          <option value={2}>2 (quick)</option>
          <option value={3}>3 (standard)</option>
          <option value={5}>5 (thorough)</option>
        </select>
        <span className="badge badge-gray">{questions.length} questions</span>
      </div>

      {result ? (
        <div className="glass-card" style={{ padding: 28 }}>
          <h2>Baseline complete — {result.correct_count}/{result.total_questions} ({result.score_percentage}%)</h2>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', margin: '16px 0' }}>
            {Object.entries(result.topic_scores || {}).map(([t, s]) => (
              <span key={t} className={`badge ${s.strength === 'strong' ? 'badge-emerald' : s.strength === 'ok' ? 'badge-indigo' : 'badge-amber'}`}>
                {t}: {s.correct}/{s.total} ({s.strength})
              </span>
            ))}
          </div>
          {(result.weak_topics?.length > 0) && <p style={{ color: '#fcd34d' }}>Weak → personalized practice: {result.weak_topics.join(', ')}</p>}
          {(result.strong_topics?.length > 0) && <p style={{ color: '#6ee7b7' }}>Strong → bypassed: {result.strong_topics.join(', ')}</p>}
          <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
            <button className="btn btn-secondary" onClick={load}>Retake baseline</button>
            <button className="btn btn-primary" onClick={() => setActiveTab('quiz')}>Start personalized practice →</button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="glass-card" style={{ padding: 28 }}>
          {questions.map((q, i) => (
            <div key={q.id + i} style={{ marginBottom: 20, padding: 16, border: '1px solid var(--border-subtle)', borderRadius: 8 }}>
              <div style={{ fontWeight: 700, marginBottom: 8 }}>#{i + 1} [{q.topic}] {q.question}</div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
                {q.options.map((opt) => (
                  <div key={opt} onClick={() => setAnswers((p) => ({ ...p, [q.id]: opt }))}
                    style={{ padding: '10px 14px', borderRadius: 8, cursor: 'pointer', border: '1px solid ' + (answers[q.id] === opt ? 'var(--primary)' : 'var(--border-subtle)'), background: answers[q.id] === opt ? 'rgba(99,102,241,.2)' : 'rgba(15,23,42,.6)' }}>
                    {opt}
                  </div>
                ))}
              </div>
            </div>
          ))}
          <button type="submit" className="btn btn-primary" disabled={submitting}>{submitting ? 'Scoring…' : 'Submit baseline'}</button>
        </form>
      )}
    </div>
  );
}
