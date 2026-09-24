import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function PreAssessment({ selectedRole, setSelectedRole, setActiveTab }) {
  const { user } = useAuth();
  const [questions, setQuestions] = useState([]);
  const [roleTopics, setRoleTopics] = useState({});
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getDiagnosticQuestions(),
      api.getRoleTopics(selectedRole)
    ])
      .then(([qData, topicsData]) => {
        setQuestions(qData);
        setRoleTopics(topicsData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedRole]);

  const handleSelectOption = (qId, option) => {
    setAnswers(prev => ({ ...prev, [qId]: option }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (Object.keys(answers).length < questions.length) {
      alert('Please answer all 10 diagnostic questions before submitting.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await api.submitDiagnostic(user?.username || 'demo_user', selectedRole, answers);
      setResult(res);
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
          <p>Complete this pre-assessment to skip topics you have already mastered at Nexora.</p>
        </div>
      </div>

      {/* Role Requirement Preview */}
      <div className="glass-card" style={{ marginBottom: '28px' }}>
        <h3 style={{ fontSize: '18px', marginBottom: '12px' }}>Role Roadmap Overview: {selectedRole}</h3>
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
        <div className="glass-card" style={{ padding: '32px', textAlign: 'center', border: '1px solid var(--accent-emerald)' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🎉</div>
          <h2 style={{ fontSize: '24px', color: '#6ee7b7', marginBottom: '12px' }}>Diagnostic Complete!</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '15px', maxWidth: '600px', margin: '0 auto 24px auto' }}>
            Our deterministic adaptive engine evaluated your answers. Topics where you demonstrated full competency are automatically bypassed.
          </p>

          {result.bypassed_titles && result.bypassed_titles.length > 0 ? (
            <div style={{ marginBottom: '28px' }}>
              <span className="badge badge-emerald" style={{ fontSize: '13px', padding: '6px 14px', marginBottom: '14px' }}>
                ✅ Bypassed Competencies ({result.bypassed_titles.length}):
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
            <p style={{ color: '#fcd34d', marginBottom: '24px' }}>
              No topics bypassed. You will start with the fundamental prerequisite modules!
            </p>
          )}

          <button
            className="btn btn-primary"
            style={{ padding: '12px 28px', fontSize: '16px' }}
            onClick={() => setActiveTab('learning-path')}
          >
            Go to Your Personalized Learning Roadmap →
          </button>
        </div>
      ) : (
        /* Questions Form */
        <form onSubmit={handleSubmit} className="glass-card" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
            <h3 style={{ fontSize: '18px' }}>10 Diagnostic Questions</h3>
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
              {submitting ? <div className="spinner"></div> : 'Submit Pre-Assessment'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
