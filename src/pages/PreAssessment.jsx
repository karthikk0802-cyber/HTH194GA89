import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function PreAssessment({ selectedRole, setSelectedRole, setActiveTab }) {
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
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <div className="spinner" style={{ width: '36px', height: '36px' }}></div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Step 1: Role & Diagnostic Pre-Assessment</h1>
          <p>Complete this pre-assessment to skip topics you have already mastered and earn starting XP points.</p>
        </div>
      </div>

      {/* Role Requirement Preview */}
      <div className="glass-card" style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '12px' }}>
          <h3 style={{ fontSize: '18px' }}>Role Roadmap Overview: {selectedRole}</h3>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>QUESTION COUNT:</span>
            <select
              className="form-select"
              style={{ width: 'auto', padding: '6px 12px', fontSize: '13px' }}
              value={questionCount}
              onChange={(e) => setQuestionCount(Number(e.target.value))}
              disabled={submitting}
            >
              <option value={5}>5 Questions (Quick)</option>
              <option value={10}>10 Questions (Standard)</option>
              <option value={15}>15 Questions (Comprehensive)</option>
            </select>
          </div>
        </div>

        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '16px' }}>
          Based on your position, you will be assigned the following required topic modules:
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          {Object.entries(roleTopics).map(([tId, tData]) => (
            <div
              key={tId}
              style={{
                padding: '8px 14px',
                background: 'rgba(99, 102, 241, 0.1)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                borderRadius: 'var(--radius-md)',
                fontSize: '13px'
              }}
            >
              <strong>{tData.title}</strong>
              {tData.prerequisites?.length > 0 && (
                <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginLeft: '6px' }}>
                  (Req: {tData.prerequisites.join(', ')})
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Result Card if submitted */}
      {result ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="glass-card" style={{ padding: '32px', textAlign: 'center', border: '1px solid var(--accent-emerald)' }}>
            <div style={{ fontSize: '48px', marginBottom: '12px' }}>🎉</div>
            <h2 style={{ fontSize: '26px', color: '#6ee7b7', marginBottom: '8px' }}>Pre-Assessment Complete!</h2>
            
            {/* Score & XP Points Banner */}
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '24px',
              margin: '20px auto',
              flexWrap: 'wrap'
            }}>
              <div style={{
                padding: '12px 24px',
                background: 'rgba(99, 102, 241, 0.2)',
                border: '1px solid rgba(99, 102, 241, 0.4)',
                borderRadius: 'var(--radius-lg)',
                textAlign: 'center'
              }}>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600, display: 'block' }}>SCORE / MARKS</span>
                <span style={{ fontSize: '28px', fontWeight: 800, color: '#ffffff' }}>
                  {result.correct_count} / {result.total_questions} ({result.score_percentage}%)
                </span>
              </div>

              <div style={{
                padding: '12px 24px',
                background: 'rgba(16, 185, 129, 0.2)',
                border: '1px solid rgba(16, 185, 129, 0.4)',
                borderRadius: 'var(--radius-lg)',
                textAlign: 'center'
              }}>
                <span style={{ fontSize: '12px', color: '#6ee7b7', fontWeight: 600, display: 'block' }}>XP EARNED & ADDED</span>
                <span style={{ fontSize: '28px', fontWeight: 800, color: '#34d399' }}>
                  +{result.xp_gained} XP ⚡
                </span>
              </div>

              <div style={{
                padding: '12px 24px',
                background: 'rgba(245, 158, 11, 0.2)',
                border: '1px solid rgba(245, 158, 11, 0.4)',
                borderRadius: 'var(--radius-lg)',
                textAlign: 'center'
              }}>
                <span style={{ fontSize: '12px', color: '#fcd34d', fontWeight: 600, display: 'block' }}>CURRENT TOTAL XP</span>
                <span style={{ fontSize: '28px', fontWeight: 800, color: '#fbbf24' }}>
                  {result.total_xp} XP (Lvl {result.level})
                </span>
              </div>
            </div>

            {result.bypassed_titles && result.bypassed_titles.length > 0 ? (
              <div style={{ marginBottom: '24px' }}>
                <span className="badge badge-emerald" style={{ fontSize: '14px', padding: '8px 16px', marginBottom: '14px' }}>
                  ✅ Automatically Bypassed Competencies ({result.bypassed_titles.length}):
                </span>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '10px', flexWrap: 'wrap', marginTop: '12px' }}>
                  {result.bypassed_titles.map((title, i) => (
                    <span key={i} className="badge badge-emerald" style={{ fontSize: '14px', padding: '8px 16px' }}>
                      {title}
                    </span>
                  ))}
                </div>
              </div>
            ) : (
              <p style={{ color: '#fcd34d', marginBottom: '20px' }}>
                No topics bypassed yet. You will start with the fundamental prerequisite modules!
              </p>
            )}

            <div style={{ display: 'flex', justifyContent: 'center', gap: '14px', flexWrap: 'wrap' }}>
              <button
                className="btn btn-secondary"
                style={{ padding: '12px 24px', fontSize: '15px' }}
                onClick={loadQuestions}
              >
                🔄 Retake Pre-Assessment
              </button>
              <button
                className="btn btn-primary"
                style={{ padding: '12px 28px', fontSize: '15px' }}
                onClick={() => setActiveTab('learning-path')}
              >
                Go to Your Personalized Learning Roadmap →
              </button>
            </div>
          </div>

          {/* Question-by-Question Evaluation Breakdown */}
          {result.evaluations && result.evaluations.length > 0 && (
            <div className="glass-card" style={{ padding: '28px' }}>
              <h3 style={{ fontSize: '18px', marginBottom: '18px', color: '#ffffff' }}>
                📋 Detailed Answers & Explanations Review
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {result.evaluations.map((ev, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '16px 20px',
                      borderRadius: 'var(--radius-md)',
                      background: ev.is_correct ? 'rgba(16, 185, 129, 0.06)' : 'rgba(239, 68, 68, 0.06)',
                      border: `1px solid ${ev.is_correct ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                      <div style={{ fontSize: '14px', fontWeight: 700, color: '#ffffff' }}>
                        <span style={{ color: ev.is_correct ? '#34d399' : '#f87171', marginRight: '8px' }}>
                          {ev.is_correct ? '✓ Correct' : '✗ Incorrect'} (#{i + 1})
                        </span>
                        {ev.question}
                      </div>
                      <span className="badge badge-gray" style={{ fontSize: '11px' }}>{ev.topic_title}</span>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '13px', margin: '8px 0' }}>
                      <div>
                        <span style={{ color: 'var(--text-muted)' }}>Your Answer: </span>
                        <strong style={{ color: ev.is_correct ? '#6ee7b7' : '#fca5a5' }}>{ev.user_answer || 'None'}</strong>
                      </div>
                      <div>
                        <span style={{ color: 'var(--text-muted)' }}>Correct Policy Answer: </span>
                        <strong style={{ color: '#6ee7b7' }}>{ev.correct_answer}</strong>
                      </div>
                    </div>

                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', background: 'rgba(0,0,0,0.2)', padding: '8px 12px', borderRadius: '4px', marginTop: '6px' }}>
                      💡 <em>{ev.explanation}</em>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Questions Form */
        <form onSubmit={handleSubmit} className="glass-card" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
            <h3 style={{ fontSize: '18px' }}>{questions.length} Diagnostic Questions</h3>
            <span className="badge badge-indigo">
              {Object.keys(answers).length} of {questions.length} Answered
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
            {questions.map((q, idx) => (
              <div
                key={q.id}
                style={{
                  padding: '20px',
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-lg)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div style={{ fontSize: '15px', fontWeight: 700, color: '#ffffff' }}>
                    <span style={{ color: 'var(--primary)', marginRight: '8px' }}>#{idx + 1}</span>
                    {q.question}
                  </div>
                  <span className="badge badge-gray">{q.topic_title}</span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
                  {q.options.map((opt, oIdx) => {
                    const isSelected = answers[q.id] === opt;
                    return (
                      <div
                        key={oIdx}
                        onClick={() => handleSelectOption(q.id, opt)}
                        style={{
                          padding: '12px 16px',
                          borderRadius: 'var(--radius-md)',
                          background: isSelected ? 'rgba(99, 102, 241, 0.2)' : 'rgba(15, 23, 42, 0.6)',
                          border: '1px solid ' + (isSelected ? 'var(--primary)' : 'var(--border-subtle)'),
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '10px',
                          color: isSelected ? '#ffffff' : 'var(--text-secondary)',
                          transition: 'all 0.2s ease'
                        }}
                      >
                        <div style={{
                          width: '18px',
                          height: '18px',
                          borderRadius: '50%',
                          border: '2px solid ' + (isSelected ? 'var(--primary)' : 'var(--text-muted)'),
                          background: isSelected ? 'var(--primary)' : 'transparent',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}>
                          {isSelected && <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#ffffff' }}></div>}
                        </div>
                        <span style={{ fontSize: '14px', fontWeight: isSelected ? 600 : 400 }}>{opt}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '32px', textAlign: 'right' }}>
            <button
              type="submit"
              className="btn btn-primary"
              style={{ padding: '12px 32px', fontSize: '15px' }}
              disabled={submitting}
            >
              {submitting ? <div className="spinner"></div> : 'Submit Pre-Assessment & Calculate Marks'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
