import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

// V2 baseline: per-topic general questions for the role card, then strength profile.
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

  if (loading) return <span className="spinner spinner-lg" />;

  return (
    <div>
      <div className="page-header">
        <h1><span className="kicker">01</span>Baseline</h1>
        <p>Role card: {selectedRole}. General questions per required topic — strengths bypass, weaknesses get targeted practice.</p>
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">02</span>Calibration</h3>
          <span className="row">
            <span className="note">Per topic</span>
            <select className="form-select" style={{ width: 'auto' }} value={perTopic} onChange={(e) => setPerTopic(Number(e.target.value))}>
              <option value={2}>2 — quick</option>
              <option value={3}>3 — standard</option>
              <option value={5}>5 — thorough</option>
            </select>
          </span>
        </div>
        <p className="sub">{questions.length} questions</p>
      </div>

      {result ? (
        <div className="section">
          <div className="sec-head">
            <h3><span className="idx">03</span>Profile</h3>
          </div>
          <p className="kpi">{result.correct_count} / {result.total_questions}</p>
          <p className="sub">{result.score_percentage}%</p>
          <div className="mt">
            {Object.entries(result.topic_scores || {}).map(([t, s]) => (
              <div key={t} className="dir-row">
                <div>
                  <div className="dir-main">{t}</div>
                  <div className="dir-sub">{s.correct}/{s.total} · {s.strength}</div>
                </div>
              </div>
            ))}
          </div>
          {result.weak_topics?.length > 0 && <p className="sub mt">Weak → personalized practice: {result.weak_topics.join(', ')}</p>}
          {result.strong_topics?.length > 0 && <p className="sub">Strong → bypassed: {result.strong_topics.join(', ')}</p>}
          <div className="row mt">
            <button className="btn btn-secondary" onClick={load}>Retake</button>
            <button className="btn btn-primary" onClick={() => setActiveTab('quiz')}>Start personalized practice →</button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="section">
          <div className="sec-head">
            <h3><span className="idx">03</span>{questions.length} questions</h3>
            <span className="note">{Object.keys(answers).length} answered</span>
          </div>
          {questions.map((q, i) => (
            <div key={q.id + i} style={{ marginBottom: 28 }}>
              <p style={{ fontSize: '1.15rem', maxWidth: '38ch' }}>
                <span className="mono" style={{ color: 'var(--accent)', marginRight: 8 }}>#{i + 1}</span>
                {q.question}
              </p>
              <p className="sub">{q.topic}</p>
              <div style={{ marginTop: 8 }}>
                {q.options.map((opt) => (
                  <div
                    key={opt}
                    onClick={() => setAnswers((p) => ({ ...p, [q.id]: opt }))}
                    className={`option${answers[q.id] === opt ? ' option-picked' : ''}`}
                  >
                    {opt}
                  </div>
                ))}
              </div>
            </div>
          ))}
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'Scoring…' : 'Submit baseline'}
          </button>
        </form>
      )}
    </div>
  );
}
