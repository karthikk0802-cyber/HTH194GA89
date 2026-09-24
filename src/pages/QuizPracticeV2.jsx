import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

// V2 practice: auto next-topic (weakness-weighted) + auto difficulty, 20-question sessions.
export default function QuizPracticeV2({ selectedRole }) {
  const { user, refreshProfile } = useAuth();
  const [next, setNext] = useState(null);
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
    try {
      const nxt = await api.getQuizNext(user?.username || 'demo_user', selectedRole);
      const res = await api.startPersonalizedSession(nxt.topic_id, selectedRole, user?.username || 'demo_user', 20);
      setSession({ ...res, _topic: nxt.topic_id });
      setNext(nxt);
    } catch (err) {
      alert('V2 session failed: ' + err.message);
    } finally {
      setSessLoading(false);
    }
  };

  const checkSessionAnswer = async () => {
    if (!sessPicked || !session || sessResult) return;
    const q = session.questions[sessIdx];
    try {
      const res = await api.submitQuiz(user?.username || 'demo_user', session._topic || 'company_basics', sessPicked, q.correct_answer);
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

  return (
    <div>
      <div className="page-header">
        <h1><span className="kicker">01</span>Personalized practice</h1>
        <p>Weakness-targeted topics, difficulty set from your mastery. Twenty unique questions per session.</p>
      </div>

      <div className="section">
        <button className="btn btn-primary" onClick={startSession} disabled={sessLoading}>
          {sessLoading ? <span className="spinner" /> : 'Start 20-question session'}
        </button>
        {next && <span className="mono mt" style={{ display: 'block', fontSize: 12, color: 'var(--muted)' }}>{next.topic_id} · {next.difficulty} · {next.reason}</span>}
      </div>

      {session && !sessDone && (
        <div className="section">
          <div className="sec-head">
            <h3><span className="idx">02</span>Question {sessIdx + 1} of {session.questions.length}</h3>
            <span className="note">Score {sessScore}</span>
          </div>
          <div className="progress">
            <div style={{ width: `${(sessIdx / session.questions.length) * 100}%` }} />
          </div>
          <p style={{ fontSize: '1.3rem', maxWidth: '36ch' }}>{session.questions[sessIdx].question}</p>
          <div style={{ marginTop: 16 }}>
            {session.questions[sessIdx].options?.map((opt) => {
              const isPicked = sessPicked === opt;
              const isCorrectOpt = opt === session.questions[sessIdx].correct_answer;
              let cls = 'option';
              if (sessResult) {
                cls += ' option-locked';
                if (isCorrectOpt) cls += ' option-right';
                else if (isPicked) cls += ' option-wrong';
              } else if (isPicked) cls += ' option-picked';
              return (
                <div key={opt} className={cls} onClick={() => !sessResult && setSessPicked(opt)}>
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
              <button className="btn btn-primary" onClick={checkSessionAnswer} disabled={!sessPicked}>Check answer</button>
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
            <h3><span className="idx">03</span>Session complete</h3>
          </div>
          <p className="kpi">{sessScore} / {session.questions.length}</p>
          <button className="btn btn-primary mt" onClick={startSession}>New 20-question set</button>
        </div>
      )}
    </div>
  );
}
