import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

const TOPIC_ID_MAP = {
  'Company Basics': 'company_basics',
  'Security & Compliance': 'security',
  'Tools & Workflows': 'tools',
  'Git Workflow': 'git_workflow',
  'Architecture Standards': 'architecture',
  'Deployment & CI/CD': 'deployment',
  'Product Triage': 'product_triage',
  'Sales Playbook': 'sales_playbook'
};

export default function QuizPractice({ selectedRole, selectedQuizTopic }) {
  const { user, refreshProfile } = useAuth();
  const [topic, setTopic] = useState(selectedQuizTopic || 'Company Basics');
  const [difficulty, setDifficulty] = useState('Beginner');

  // 20-question session state (no-repeat set fetched once)
  const [session, setSession] = useState(null);
  const [sessIdx, setSessIdx] = useState(0);
  const [sessPicked, setSessPicked] = useState('');
  const [sessScore, setSessScore] = useState(0);
  const [sessDone, setSessDone] = useState(false);
  const [sessLoading, setSessLoading] = useState(false);
  // per-question validation + teaching
  const [sessResult, setSessResult] = useState(null);
  const [sessRemediation, setSessRemediation] = useState(null);
  const [sessExplainAgain, setSessExplainAgain] = useState(null);
  const [sessLoadingExplain, setSessLoadingExplain] = useState(false);

  // Feedback form (report inaccurate session question)
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackReason, setFeedbackReason] = useState('Unclear/Ambiguous');
  const [feedbackComments, setFeedbackComments] = useState('');
  const [feedbackSuccess, setFeedbackSuccess] = useState(false);

  const topicsList = [
    'Company Basics',
    'Security & Compliance',
    'Git Workflow',
    'Deployment & CI/CD',
    'Architecture Standards',
    'Tools & Workflows',
    'Product Triage',
    'Sales Playbook'
  ];

  useEffect(() => {
    if (selectedQuizTopic) {
      setTopic(selectedQuizTopic);
    }
  }, [selectedQuizTopic]);

  const startSession = async () => {
    setSessLoading(true);
    setSession(null);
    setSessIdx(0);
    setSessPicked('');
    setSessScore(0);
    setSessDone(false);
    setSessResult(null);
    setSessRemediation(null);
    setSessExplainAgain(null);
    setFeedbackSuccess(false);
    try {
      const res = await api.startQuizSession(topic, selectedRole, difficulty, 20);
      setSession(res);
    } catch (err) {
      alert('Failed to start session: ' + err.message);
    } finally {
      setSessLoading(false);
    }
  };

  const checkSessionAnswer = async () => {
    if (!sessPicked || !session || sessResult) return;
    const q = session.questions[sessIdx];
    try {
      const topicId = TOPIC_ID_MAP[topic] || topic.toLowerCase().replace(/ & /g, '_').replace(/ /g, '_');
      const res = await api.submitQuiz(user?.username || 'demo_user', topicId, sessPicked, q.correct_answer);
      setSessResult(res);
      if (res.is_correct) {
        setSessScore((s) => s + 1);
      } else {
        const rem = await api.getRemediation(q.question, sessPicked, q.correct_answer, q.evidence_quote || '');
        setSessRemediation(rem);
      }
      if (res.xp_gained > 0) refreshProfile();
    } catch (err) {
      console.warn('Session answer submit failed:', err);
    }
  };

  const advanceSession = () => {
    if (!session) return;
    if (sessIdx + 1 >= session.questions.length) {
      setSessDone(true);
    } else {
      setSessIdx((i) => i + 1);
      setSessPicked('');
      setSessResult(null);
      setSessRemediation(null);
      setSessExplainAgain(null);
    }
  };

  const explainSessionAgain = async () => {
    if (!session) return;
    const q = session.questions[sessIdx];
    setSessLoadingExplain(true);
    try {
      const prev = sessRemediation ? `${sessRemediation.why_incorrect} ${sessRemediation.why_correct}` : '';
      const res = await api.getExplainAgain(q.question, sessPicked, q.correct_answer, prev);
      setSessExplainAgain(res.explanation);
    } catch (err) {
      alert('Error generating ELI5 explanation: ' + err.message);
    } finally {
      setSessLoadingExplain(false);
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    if (!session) return;
    try {
      await api.submitQuizFeedback(session.questions[sessIdx].question, feedbackReason, feedbackComments);
      setFeedbackSuccess(true);
      setTimeout(() => {
        setShowFeedbackModal(false);
        setFeedbackSuccess(false);
      }, 2000);
    } catch (err) {
      alert('Error sending feedback: ' + err.message);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Adaptive Practice & Remediation</h1>
          <p>20-question sessions with unique grounded questions, instant validation, and automated coaching.</p>
        </div>
      </div>

      {/* Session Setup Controls */}
      <div className="glass-card" style={{ marginBottom: '28px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr) auto', gap: '16px', alignItems: 'flex-end' }}>
          <div className="input-group" style={{ marginBottom: 0 }}>
            <label className="input-label">Select Practice Topic</label>
            <select className="form-select" value={topic} onChange={(e) => setTopic(e.target.value)}>
              {topicsList.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          <div className="input-group" style={{ marginBottom: 0 }}>
            <label className="input-label">Difficulty Level</label>
            <select className="form-select" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
              <option value="Beginner">Beginner (Foundations)</option>
              <option value="Intermediate">Intermediate (Practitioner)</option>
              <option value="Expert">Expert (Edge Cases & Arch)</option>
            </select>
          </div>

          <div className="input-group" style={{ marginBottom: 0 }}>
            <label className="input-label">Role Context</label>
            <input type="text" disabled className="form-input" value={selectedRole} style={{ opacity: 0.8 }} />
          </div>

          <button
            className="btn btn-primary"
            style={{ padding: '12px 24px', fontSize: '15px' }}
            onClick={startSession}
            disabled={sessLoading}
          >
            {sessLoading ? <div className="spinner"></div> : '▶ Start 20-question session'}
          </button>
        </div>
      </div>

      {!session && !sessLoading && (
        <div className="glass-card" style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📝</div>
          <h3 style={{ fontSize: '20px', color: '#ffffff', marginBottom: '8px' }}>Ready to practice?</h3>
          <p style={{ maxWidth: '500px', margin: '0 auto 24px auto', fontSize: '14px' }}>
            Select a topic and difficulty above, then start a 20-question session. Every question is unique —
            no repeats — with instant right/wrong validation, remediation coaching, and ELI5 explanations.
          </p>
          <button className="btn btn-primary" onClick={startSession}>
            Start 20-question session now
          </button>
        </div>
      )}

      {session && !sessDone && (
        <div className="glass-card" style={{ padding: '32px', marginBottom: '28px' }}>
          <div style={{ height: 8, background: 'rgba(255,255,255,0.08)', borderRadius: 4, marginBottom: 20 }}>
            <div style={{ width: `${((sessIdx) / session.questions.length) * 100}%`, height: '100%', background: 'var(--primary)', borderRadius: 4, transition: 'width .3s' }} />
          </div>
          {/* Header & Badges */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
            <div>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '8px', flexWrap: 'wrap' }}>
                <span className="badge badge-indigo">{topic}</span>
                <span className="badge badge-cyan">{difficulty} Level</span>
                <span className="badge badge-gray">Q {sessIdx + 1} / {session.questions.length} · Score {sessScore}</span>
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                🎯 <strong>Learning Objective:</strong> {session.questions[sessIdx].learning_objective || 'Demonstrate mastery of Nexora operating policies.'}
              </p>
            </div>
            <button
              className="btn btn-secondary"
              style={{ padding: '6px 12px', fontSize: '12px' }}
              onClick={() => setShowFeedbackModal(true)}
            >
              🚩 Report Question
            </button>
          </div>

          {/* Question Text */}
          <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '24px', lineHeight: 1.5 }}>
            {session.questions[sessIdx].question}
          </h2>

          {/* Options */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '28px' }}>
            {session.questions[sessIdx].options?.map((opt, i) => {
              const isPicked = sessPicked === opt;
              const isCorrectOpt = opt === session.questions[sessIdx].correct_answer;
              let bg = 'rgba(15, 23, 42, 0.6)';
              let border = 'var(--border-subtle)';
              if (sessResult) {
                if (isCorrectOpt) {
                  bg = 'rgba(16, 185, 129, 0.15)';
                  border = 'var(--accent-emerald)';
                } else if (isPicked && !sessResult.is_correct) {
                  bg = 'rgba(239, 68, 68, 0.15)';
                  border = 'var(--accent-rose)';
                }
              } else if (isPicked) {
                bg = 'rgba(99, 102, 241, 0.2)';
                border = 'var(--primary)';
              }
              return (
                <div
                  key={i}
                  onClick={() => !sessResult && setSessPicked(opt)}
                  style={{
                    padding: '16px 20px',
                    borderRadius: 'var(--radius-md)',
                    background: bg,
                    border: '1px solid ' + border,
                    cursor: sessResult ? 'default' : 'pointer',
                    fontSize: '15px', color: '#ffffff'
                  }}
                >
                  {opt}
                </div>
              );
            })}
          </div>

          {/* Immediate validation banner */}
          {sessResult && (
            <div style={{
              padding: '20px',
              borderRadius: 'var(--radius-md)',
              background: sessResult.is_correct ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
              border: '1px solid ' + (sessResult.is_correct ? 'var(--accent-emerald)' : 'var(--accent-rose)'),
              marginBottom: '24px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{ fontSize: '24px' }}>{sessResult.is_correct ? '✅' : '❌'}</span>
                  <div>
                    <h3 style={{ fontSize: '18px', color: sessResult.is_correct ? '#6ee7b7' : '#fca5a5' }}>
                      {sessResult.is_correct ? 'Right! Excellent mastery.' : 'Wrong answer.'}
                    </h3>
                    <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                      Mastery Score: <strong>{sessResult.mastery_score}/100</strong> • Status: <strong>{sessResult.status}</strong>
                    </p>
                  </div>
                </div>
                {sessResult.xp_gained > 0 && (
                  <span className="badge badge-indigo" style={{ fontSize: '14px', padding: '6px 14px' }}>
                    +{sessResult.xp_gained} XP Earned! ⚡
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Why it's wrong + teaching remediation */}
          {sessResult && !sessResult.is_correct && sessRemediation && (
            <div className="glass-card" style={{ background: 'rgba(15, 23, 42, 0.9)', borderLeft: '4px solid var(--accent-amber)', marginBottom: '24px' }}>
              <h3 style={{ fontSize: '18px', color: '#fcd34d', marginBottom: '14px' }}>📚 Why it's wrong</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '14px', lineHeight: 1.6 }}>
                <div>
                  <strong style={{ color: '#fca5a5' }}>Why your choice doesn't fit:</strong> {sessRemediation.why_incorrect}
                </div>
                <div>
                  <strong style={{ color: '#6ee7b7' }}>Correct policy rationale:</strong> {sessRemediation.why_correct}
                </div>
                <div style={{ padding: '12px 16px', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '8px', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
                  💡 <strong>Memory Hook:</strong> {sessRemediation.memory_hook}
                </div>
              </div>
              <div style={{ marginTop: '16px' }}>
                <button
                  className="btn btn-secondary"
                  onClick={explainSessionAgain}
                  disabled={sessLoadingExplain}
                >
                  {sessLoadingExplain ? <div className="spinner"></div> : '🤔 Still confused? Explain again (ELI5)'}
                </button>
              </div>
              {sessExplainAgain && (
                <div style={{ marginTop: '16px', padding: '14px 18px', background: 'rgba(245, 158, 11, 0.08)', borderRadius: '8px', border: '1px solid rgba(245, 158, 11, 0.25)' }}>
                  <h4 style={{ fontSize: '14px', color: '#fcd34d', marginBottom: '6px' }}>💡 Simplified Analogy (ELI5):</h4>
                  <p style={{ fontSize: '14px', color: '#f9fafb', lineHeight: 1.6 }}>{sessExplainAgain}</p>
                </div>
              )}
            </div>
          )}

          <div style={{ textAlign: 'right' }}>
            {!sessResult ? (
              <button
                className="btn btn-primary"
                style={{ padding: '12px 32px', fontSize: '15px' }}
                onClick={checkSessionAnswer}
                disabled={!sessPicked}
              >
                Check answer
              </button>
            ) : (
              <button
                className="btn btn-primary"
                style={{ padding: '12px 32px', fontSize: '15px' }}
                onClick={advanceSession}
              >
                {sessIdx + 1 >= session.questions.length ? 'See final score' : 'Next question →'}
              </button>
            )}
          </div>
        </div>
      )}

      {session && sessDone && (
        <div className="glass-card" style={{ padding: '40px', marginBottom: '28px', textAlign: 'center' }}>
          <div style={{ fontSize: 48 }}>🎉</div>
          <h2>Session complete: {sessScore} / {session.questions.length} ({Math.round((sessScore / session.questions.length) * 100)}%)</h2>
          <p style={{ color: 'var(--text-secondary)', margin: '12px 0 24px' }}>
            {sessScore === session.questions.length ? 'Perfect mastery of this topic.' : sessScore >= session.questions.length * 0.8 ? 'Strong — review the ones you missed.' : 'Keep practicing — weak areas were logged to your learning path.'}
          </p>
          <button className="btn btn-primary" onClick={startSession}>↻ New 20-question set</button>
        </div>
      )}

      {/* Feedback Modal */}
      {showFeedbackModal && session && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px'
        }}>
          <div className="glass-card" style={{ width: '100%', maxWidth: '500px', padding: '28px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ fontSize: '18px' }}>Report Question Inaccuracy</h3>
              <button
                style={{ background: 'none', border: 'none', color: '#9ca3af', fontSize: '18px', cursor: 'pointer' }}
                onClick={() => setShowFeedbackModal(false)}
              >
                ✕
              </button>
            </div>

            {feedbackSuccess ? (
              <div style={{ padding: '20px', textAlign: 'center', color: '#6ee7b7' }}>
                ✓ Thank you! Your feedback was logged for admin audit review.
              </div>
            ) : (
              <form onSubmit={handleSubmitFeedback}>
                <div className="input-group">
                  <label className="input-label">Reason</label>
                  <select
                    className="form-select"
                    value={feedbackReason}
                    onChange={(e) => setFeedbackReason(e.target.value)}
                  >
                    <option value="Outdated">Outdated Policy</option>
                    <option value="Conflict with other policy">Conflict with another policy</option>
                    <option value="Unclear/Ambiguous">Unclear or Ambiguous Wording</option>
                  </select>
                </div>

                <div className="input-group">
                  <label className="input-label">Additional Comments</label>
                  <textarea
                    className="form-textarea"
                    placeholder="Provide details on what seems inaccurate or confusing..."
                    value={feedbackComments}
                    onChange={(e) => setFeedbackComments(e.target.value)}
                  ></textarea>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                  <button type="button" className="btn btn-secondary" onClick={() => setShowFeedbackModal(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Submit Report
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
