import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function PreAssessment({ selectedRole, setActiveTab }) {
  const { user, updateXpPoints, refreshProfile } = useAuth();
  const [questionCount, setQuestionCount] = useState(10);
  const [questions, setQuestions] = useState([]);
  const [roleTopics, setRoleTopics] = useState({});
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  const loadQuestions = () => {
    setLoading(true);
    setResult(null);
    setAnswers({});
    Promise.all([
      api.getDiagnosticQuestions(selectedRole, questionCount),
      api.getRoleTopics(selectedRole)
    ])
      .then(([qData, topicsData]) => {
        setQuestions(qData);
        setRoleTopics(topicsData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadQuestions();
  }, [selectedRole, questionCount]);

  const handleSelectOption = (qId, option) => {
    setAnswers(prev => ({ ...prev, [qId]: option }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const answeredCount = Object.keys(answers).length;
    if (answeredCount < questions.length) {
      const confirmSubmit = window.confirm(`You have answered ${answeredCount} of ${questions.length} questions. Unanswered questions will be marked as incorrect. Submit anyway?`);
      if (!confirmSubmit) return;
    }

    setSubmitting(true);
    try {
      const res = await api.submitDiagnostic(user?.username || 'demo_user', selectedRole, answers);
      setResult(res);
      if (res.total_xp !== undefined) {
        updateXpPoints(res.total_xp, res.level);
      } else if (res.xp_gained) {
        refreshProfile();
      }
    } catch (err) {
      alert('Error evaluating diagnostic: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <span className="spinner spinner-lg" />;
  }

  return (
    <div>
      <div className="page-header">
        <h1><span className="kicker">01</span>Pre-Assessment</h1>
        <p>Role: {selectedRole}. Skip what you've mastered, earn starting XP.</p>
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">02</span>Required modules</h3>
          <span className="row">
            <span className="note">Length</span>
            <select
              className="form-select"
              style={{ width: 'auto' }}
              value={questionCount}
              onChange={(e) => setQuestionCount(Number(e.target.value))}
              disabled={submitting}
            >
              <option value={5}>5 — quick</option>
              <option value={10}>10 — standard</option>
              <option value={15}>15 — comprehensive</option>
            </select>
          </span>
        </div>
        <div>
          {Object.entries(roleTopics).map(([tId, tData]) => (
            <div key={tId} className="dir-row">
              <div>
                <div className="dir-main">{tData.title}</div>
                {tData.prerequisites?.length > 0 && (
                  <div className="dir-sub">Requires {tData.prerequisites.join(', ')}</div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {result ? (
        <div className="section">
          <div className="sec-head">
            <h3><span className="idx">03</span>Result</h3>
          </div>
          <p className="kpi">{result.correct_count} / {result.total_questions}</p>
          <p className="sub">{result.score_percentage}% · +{result.xp_gained} XP · {result.total_xp} total (Level {result.level})</p>

          {result.bypassed_titles && result.bypassed_titles.length > 0 ? (
            <div className="mt">
              {result.bypassed_titles.map((title, i) => (
                <div key={i} className="dir-row">
                  <div>
                    <div className="dir-main">{title}</div>
                    <div className="dir-sub">Bypassed</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="sub">No topics bypassed. You'll start from the fundamentals.</p>
          )}

          <div className="row mt">
            <button className="btn btn-secondary" onClick={loadQuestions}>Retake</button>
            <button className="btn btn-primary" onClick={() => setActiveTab('learning-path')}>
              Your learning roadmap →
            </button>
          </div>

          {result.evaluations && result.evaluations.length > 0 && (
            <div className="section mt">
              <div className="sec-head">
                <h3><span className="idx">04</span>Answer review</h3>
              </div>
              <div>
                {result.evaluations.map((ev, i) => (
                  <div key={i} className="dir-row">
                    <div>
                      <div>
                        <div className="dir-main">#{i + 1} — {ev.question}</div>
                        <div className="dir-sub">
                          {ev.is_correct ? 'Correct' : 'Incorrect'} · You: {ev.user_answer || '—'} · Answer: {ev.correct_answer}
                        </div>
                        <div className="dir-sub">{ev.explanation}</div>
                      </div>
                      <span className="badge badge-gray">{ev.topic_title}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="section">
          <div className="sec-head">
            <h3><span className="idx">03</span>{questions.length} questions</h3>
            <span className="note">{Object.keys(answers).length} answered</span>
          </div>
          {questions.map((q, idx) => (
            <div key={q.id} style={{ marginBottom: 28 }}>
              <p style={{ fontSize: '1.15rem', maxWidth: '38ch' }}>
                <span className="mono" style={{ color: 'var(--accent)', marginRight: 8 }}>#{idx + 1}</span>
                {q.question}
              </p>
              <p className="sub">{q.topic_title}</p>
              <div style={{ marginTop: 8 }}>
                {q.options.map((opt, oIdx) => {
                  const isSelected = answers[q.id] === opt;
                  return (
                    <div
                      key={oIdx}
                      onClick={() => handleSelectOption(q.id, opt)}
                      className={`option${isSelected ? ' option-picked' : ''}`}
                    >
                      {opt}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? <span className="spinner" /> : 'Submit & calculate marks'}
          </button>
        </form>
      )}
    </div>
  );
}
