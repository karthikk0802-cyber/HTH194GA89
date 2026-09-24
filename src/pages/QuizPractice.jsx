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
  const [loading, setLoading] = useState(false);
  const [quiz, setQuiz] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);
  
  // Remediation & ELI5
  const [remediation, setRemediation] = useState(null);
  const [explainAgain, setExplainAgain] = useState(null);
  const [loadingExplain, setLoadingExplain] = useState(false);

  // Feedback form
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

  const handleGenerate = async () => {
    setLoading(true);
    setQuiz(null);
    setSelectedAnswer('');
    setSubmissionResult(null);
    setRemediation(null);
    setExplainAgain(null);
    setFeedbackSuccess(false);

    try {
      const res = await api.generateQuiz(topic, selectedRole, difficulty);
      setQuiz(res);
    } catch (err) {
      alert('Failed to generate quiz: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!selectedAnswer) {
      alert('Please select an option before submitting.');
      return;
    }

    setSubmitting(true);
    try {
      const topicId = TOPIC_ID_MAP[topic] || topic.toLowerCase().replace(/ & /g, '_').replace(/ /g, '_');
      const res = await api.submitQuiz(user?.username || 'demo_user', topicId, selectedAnswer, quiz.correct_answer);
      setSubmissionResult(res);
      if (res.xp_gained > 0) {
        refreshProfile();
      }

      if (!res.is_correct) {
        // Fetch remediation
        const rem = await api.getRemediation(quiz.question, selectedAnswer, quiz.correct_answer, quiz.evidence_quote);
        setRemediation(rem);
      }
    } catch (err) {
      alert('Error submitting answer: ' + err.message);
    } finally {
      setSubmitting(false);
    }
  };


  const handleExplainAgain = async () => {
    setLoadingExplain(true);
    try {
      const prev = remediation ? `${remediation.why_incorrect} ${remediation.why_correct}` : '';
      const res = await api.getExplainAgain(quiz.question, selectedAnswer, quiz.correct_answer, prev);
      setExplainAgain(res.explanation);
    } catch (err) {
      alert('Error generating ELI5 explanation: ' + err.message);
    } finally {
      setLoadingExplain(false);
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    try {
      await api.submitQuizFeedback(quiz.question, feedbackReason, feedbackComments);
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
          <p>Strictly RAG-grounded multiple-choice quizzes with zero-temperature validation and automated coaching.</p>
        </div>
      </div>

      {/* Generator Controls */}
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
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? <div className="spinner"></div> : '⚡ Generate Grounded Question'}
          </button>
        </div>
      </div>

      {/* Quiz Card */}
      {quiz ? (
        <div className="glass-card" style={{ padding: '32px', marginBottom: '28px' }}>
          {/* Header & Badges */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
            <div>
              <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                <span className="badge badge-indigo">{topic}</span>
                <span className="badge badge-cyan">{difficulty} Level</span>
                {quiz.validation_passed !== false && (
                  <span className="badge badge-emerald">✓ Anti-Hallucination Gate Passed</span>
                )}
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                🎯 <strong>Learning Objective:</strong> {quiz.learning_objective || 'Demonstrate mastery of Nexora operating policies.'}
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
            {quiz.question}
          </h2>

          {/* Options */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '28px' }}>
            {quiz.options?.map((opt, i) => {
              const isSelected = selectedAnswer === opt;
              let optionBg = 'rgba(15, 23, 42, 0.6)';
              let borderColor = 'var(--border-subtle)';

              if (submissionResult) {
                if (opt === quiz.correct_answer) {
                  optionBg = 'rgba(16, 185, 129, 0.15)';
                  borderColor = 'var(--accent-emerald)';
                } else if (isSelected && !submissionResult.is_correct) {
                  optionBg = 'rgba(239, 68, 68, 0.15)';
                  borderColor = 'var(--accent-rose)';
                }
              } else if (isSelected) {
                optionBg = 'rgba(99, 102, 241, 0.2)';
                borderColor = 'var(--primary)';
              }

              return (
                <div
                  key={i}
                  onClick={() => !submissionResult && setSelectedAnswer(opt)}
                  style={{
                    padding: '16px 20px',
                    borderRadius: 'var(--radius-md)',
                    background: optionBg,
                    border: '1px solid ' + borderColor,
                    cursor: submissionResult ? 'default' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    transition: 'all 0.2s ease'
                  }}
                >
                  <div style={{
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    border: '2px solid ' + (isSelected ? 'var(--primary)' : 'var(--text-muted)'),
                    background: isSelected ? 'var(--primary)' : 'transparent',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                  }}>
                    {isSelected && <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#ffffff' }}></div>}
                  </div>
                  <span style={{ fontSize: '15px', color: '#ffffff', fontWeight: isSelected ? 600 : 400 }}>
                    {opt}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Submit Action */}
          {!submissionResult ? (
            <div style={{ textAlign: 'right' }}>
              <button
                className="btn btn-primary"
                style={{ padding: '12px 32px', fontSize: '15px' }}
                onClick={handleSubmitAnswer}
                disabled={submitting || !selectedAnswer}
              >
                {submitting ? <div className="spinner"></div> : 'Submit Answer'}
              </button>
            </div>
          ) : (
            <div>
              {/* Correct / Incorrect Banner */}
              <div style={{
                padding: '20px',
                borderRadius: 'var(--radius-md)',
                background: submissionResult.is_correct ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                border: '1px solid ' + (submissionResult.is_correct ? 'var(--accent-emerald)' : 'var(--accent-rose)'),
                marginBottom: '24px'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '24px' }}>{submissionResult.is_correct ? '✅' : '❌'}</span>
                    <div>
                      <h3 style={{ fontSize: '18px', color: submissionResult.is_correct ? '#6ee7b7' : '#fca5a5' }}>
                        {submissionResult.is_correct ? 'Correct! Excellent mastery.' : 'Incorrect answer.'}
                      </h3>
                      <p style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                        Mastery Score: <strong>{submissionResult.mastery_score}/100</strong> • Status: <strong>{submissionResult.status}</strong>
                      </p>
                    </div>
                  </div>
                  {submissionResult.xp_gained > 0 && (
                    <span className="badge badge-indigo" style={{ fontSize: '14px', padding: '6px 14px' }}>
                      +{submissionResult.xp_gained} XP Earned! ⚡
                    </span>
                  )}
                </div>
              </div>

              {/* Remediation Block */}
              {remediation && (
                <div className="glass-card" style={{ background: 'rgba(15, 23, 42, 0.9)', borderLeft: '4px solid var(--accent-amber)', marginBottom: '24px' }}>
                  <h3 style={{ fontSize: '18px', color: '#fcd34d', marginBottom: '14px' }}>📚 Teaching Remediation</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '14px', lineHeight: 1.6 }}>
                    <div>
                      <strong style={{ color: '#fca5a5' }}>Why your choice doesn't fit:</strong> {remediation.why_incorrect}
                    </div>
                    <div>
                      <strong style={{ color: '#6ee7b7' }}>Correct policy rationale:</strong> {remediation.why_correct}
                    </div>
                    <div style={{ padding: '12px 16px', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '8px', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
                      💡 <strong>Memory Hook:</strong> {remediation.memory_hook}
                    </div>
                  </div>

                  {/* Explain Again (ELI5) Button */}
                  <div style={{ marginTop: '16px' }}>
                    <button
                      className="btn btn-secondary"
                      onClick={handleExplainAgain}
                      disabled={loadingExplain}
                    >
                      {loadingExplain ? <div className="spinner"></div> : '🤔 Still Confused? Explain Again (ELI5 Analogy)'}
                    </button>
                  </div>

                  {explainAgain && (
                    <div style={{ marginTop: '16px', padding: '14px 18px', background: 'rgba(245, 158, 11, 0.08)', borderRadius: '8px', border: '1px solid rgba(245, 158, 11, 0.25)' }}>
                      <h4 style={{ fontSize: '14px', color: '#fcd34d', marginBottom: '6px' }}>💡 Simplified Analogy (ELI5):</h4>
                      <p style={{ fontSize: '14px', color: '#f9fafb', lineHeight: 1.6 }}>{explainAgain}</p>
                    </div>
                  )}
                </div>
              )}

              <div style={{ textAlign: 'right' }}>
                <button
                  className="btn btn-primary"
                  style={{ padding: '12px 32px', fontSize: '15px' }}
                  onClick={handleGenerate}
                >
                  Next Practice Question →
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="glass-card" style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>📝</div>
          <h3 style={{ fontSize: '20px', color: '#ffffff', marginBottom: '8px' }}>Ready to practice?</h3>
          <p style={{ maxWidth: '500px', margin: '0 auto 24px auto', fontSize: '14px' }}>
            Select a topic and difficulty level above, then generate a verified multiple-choice question tailored to your role.
          </p>
          <button className="btn btn-primary" onClick={handleGenerate}>
            Generate Question Now
          </button>
        </div>
      )}

      {/* Feedback Modal */}
      {showFeedbackModal && (
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
