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

  const [session, setSession] = useState(null);
  const [sessIdx, setSessIdx] = useState(0);
  const [sessPicked, setSessPicked] = useState('');
  const [sessScore, setSessScore] = useState(0);
  const [sessDone, setSessDone] = useState(false);
  const [sessLoading, setSessLoading] = useState(false);
  const [sessResult, setSessResult] = useState(null);
  const [sessRemediation, setSessRemediation] = useState(null);
  const [sessExplainAgain, setSessExplainAgain] = useState(null);
  const [sessLoadingExplain, setSessLoadingExplain] = useState(false);

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
      const res = await api.startQuizSession(topic, selectedRole, user?.username || '', 20);
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
        <h1><span className="kicker">01</span>Practice</h1>
        <p>Twenty unique questions per session. Nothing repeats.</p>
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">02</span>Setup</h3>
        </div>
        <div className="grid-3">
          <div className="input-group" style={{ marginBottom: 0 }}>
            <label className="input-label">Topic</label>
            <select className="form-select" value={topic} onChange={(e) => setTopic(e.target.value)}>
              {topicsList.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="input-group" style={{ marginBottom: 0 }}>
            <label className="input-label">Role</label>
            <input type="text" disabled className="form-input" value={selectedRole} />
          </div>
          <div className="input-group" style={{ marginBottom: 0 }}>
            <label className="input-label">Difficulty</label>
            <input type="text" disabled className="form-input" value="Auto — set from your mastery" />
          </div>
        </div>
        <div className="mt">
          <button className="btn btn-primary" onClick={startSession} disabled={sessLoading}>
            {sessLoading ? <span className="spinner" /> : 'Start 20-question session'}
          </button>
        </div>
      </div>

      {!session && !sessLoading && (
        <div className="section">
          <p className="sub">Pick a topic above. Difficulty sets itself from your mastery of it. Each answer is checked instantly, with coaching when you miss.</p>
        </div>
      )}

      {session && !sessDone && (
        <div className="section">
          <div className="sec-head">
            <h3><span className="idx">03</span>Question {sessIdx + 1} of {session.questions.length}</h3>
            <span className="note">Score {sessScore} · {topic} · {session.difficulty}{session.mastery != null ? ` (mastery ${session.mastery})` : ''}</span>
          </div>
          <div className="progress">
            <div style={{ width: `${(sessIdx / session.questions.length) * 100}%` }} />
          </div>

          <p style={{ fontSize: '1.3rem', maxWidth: '36ch', marginBottom: 4 }}>
            {session.questions[sessIdx].question}
          </p>
          <p className="sub">
            {session.questions[sessIdx].learning_objective || 'Demonstrate mastery of Nexora operating policies.'}
            {' · '}
            <button onClick={() => setShowFeedbackModal(true)} style={{ background: 'none', border: 'none', padding: 0, cursor: 'pointer', color: 'var(--muted)', fontFamily: 'var(--mono)', fontSize: 12 }}>
              Report question
            </button>
          </p>

          <div style={{ marginTop: 16 }}>
            {session.questions[sessIdx].options?.map((opt, i) => {
              const isPicked = sessPicked === opt;
              const isCorrectOpt = opt === session.questions[sessIdx].correct_answer;
              let cls = 'option';
              if (sessResult) {
                cls += ' option-locked';
                if (isCorrectOpt) cls += ' option-right';
                else if (isPicked) cls += ' option-wrong';
              } else if (isPicked) cls += ' option-picked';
              return (
                <div key={i} className={cls} onClick={() => !sessResult && setSessPicked(opt)}>
                  {opt}
                </div>
              );
            })}
          </div>

          {sessResult && (
            <div className={`verdict ${sessResult.is_correct ? 'verdict-right' : 'verdict-wrong'}`}>
              <div>
                <h3>{sessResult.is_correct ? 'Right.' : 'Wrong.'}</h3>
                <p>Mastery {sessResult.mastery_score}/100 · {sessResult.status}{sessResult.xp_gained > 0 ? ` · +${sessResult.xp_gained} XP` : ''}</p>
                {session.questions[sessIdx].evidence_quote && (
                  <p className="mt">Source passage: “{session.questions[sessIdx].evidence_quote}”</p>
                )}
              </div>
            </div>
          )}

          {sessResult && !sessResult.is_correct && sessRemediation && (
            <div className="callout">
              <h4>Why it's wrong</h4>
              <p><strong>Your choice:</strong> {sessRemediation.why_incorrect}</p>
              <p className="mt"><strong>Correct rationale:</strong> {sessRemediation.why_correct}</p>
              <p className="mt"><strong>Memory hook:</strong> {sessRemediation.memory_hook}</p>
              <div className="mt">
                <button className="btn btn-sm btn-secondary" onClick={explainSessionAgain} disabled={sessLoadingExplain}>
                  {sessLoadingExplain ? <span className="spinner" /> : 'Still confused? Explain again (ELI5)'}
                </button>
              </div>
              {sessExplainAgain && (
                <div className="callout callout-info mt">
                  <h4>Simplified, like you're five</h4>
                  <p>{sessExplainAgain}</p>
                </div>
              )}
            </div>
          )}

          <div className="row-end mt">
            {!sessResult ? (
              <button className="btn btn-primary" onClick={checkSessionAnswer} disabled={!sessPicked}>
                Check answer
              </button>
            ) : (
              <button className="btn btn-primary" onClick={advanceSession}>
                {sessIdx + 1 >= session.questions.length ? 'See final score' : 'Next →'}
              </button>
            )}
          </div>
        </div>
      )}

      {session && sessDone && (
        <div className="section center">
          <div className="sec-head">
            <h3><span className="idx">04</span>Session complete</h3>
          </div>
          <p className="kpi">{sessScore} / {session.questions.length}</p>
          <p className="sub">
            {sessScore === session.questions.length ? 'Perfect mastery of this topic.' : sessScore >= session.questions.length * 0.8 ? 'Strong — review the ones you missed.' : 'Keep practicing — weak areas were logged to your learning path.'}
          </p>
          <button className="btn btn-primary mt" onClick={startSession}>New 20-question set</button>
        </div>
      )}

      {showFeedbackModal && session && (
        <div className="modal-veil">
          <div className="modal">
            <div className="modal-h">
              <h3>Report question</h3>
              <button className="modal-x" onClick={() => setShowFeedbackModal(false)}>✕</button>
            </div>
            {feedbackSuccess ? (
              <p>Logged for admin review. Thank you.</p>
            ) : (
              <form onSubmit={handleSubmitFeedback}>
                <div className="input-group">
                  <label className="input-label">Reason</label>
                  <select className="form-select" value={feedbackReason} onChange={(e) => setFeedbackReason(e.target.value)}>
                    <option value="Outdated">Outdated Policy</option>
                    <option value="Conflict with other policy">Conflict with another policy</option>
                    <option value="Unclear/Ambiguous">Unclear or Ambiguous Wording</option>
                  </select>
                </div>
                <div className="input-group">
                  <label className="input-label">Details</label>
                  <textarea className="form-textarea" value={feedbackComments} onChange={(e) => setFeedbackComments(e.target.value)} />
                </div>
                <div className="row-end">
                  <button type="button" className="btn btn-secondary" onClick={() => setShowFeedbackModal(false)}>Cancel</button>
                  <button type="submit" className="btn btn-primary">Submit report</button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
