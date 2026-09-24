import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

// V2 practice: auto next-topic (weakness-weighted) + auto difficulty.
// Generation uses v1 generate_quiz_for_topic via /api/v2/quiz/generate (shape unchanged + personalization).
// Submit reuses v1 POST /api/quiz/submit (contract frozen).
export default function QuizPracticeV2({ selectedRole }) {
  const { user, refreshProfile } = useAuth();
  const [next, setNext] = useState(null);
  // 20-question session (no-repeat set, auto difficulty)
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
        <div>
          <h1>Personalized Practice v2</h1>
          <p>Weakness-targeted topics, auto difficulty from mastery. Fully grounded, same validators as v1.</p>
        </div>
      </div>
      <div className="glass-card" style={{ marginBottom: 20 }}>
        <button className="btn btn-primary" onClick={startSession} disabled={sessLoading}>
          {sessLoading ? 'Starting…' : '▶ Start 20-question personalized session'}
        </button>
        {next && <span className="badge badge-indigo" style={{ marginLeft: 12 }}>{next.topic_id} · {next.difficulty} · {next.reason}</span>}
      </div>
      {session && !sessDone && (
        <div className="glass-card" style={{ padding: 28, marginBottom: 20 }}>
          <div style={{ height: 8, background: 'rgba(255,255,255,0.08)', borderRadius: 4, marginBottom: 20 }}>
            <div style={{ width: `${(sessIdx / session.questions.length) * 100}%`, height: '100%', background: 'var(--primary)', borderRadius: 4 }} />
          </div>
          <span className="badge badge-indigo">Q {sessIdx + 1} / {session.questions.length} · Score {sessScore}</span>
          <h2 style={{ margin: '16px 0 24px', lineHeight: 1.5 }}>{session.questions[sessIdx].question}</h2>
          {session.questions[sessIdx].options?.map((opt) => {
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
              bg = 'rgba(99,102,241,.2)';
              border = 'var(--primary)';
            }
            return (
              <div key={opt} onClick={() => !sessResult && setSessPicked(opt)}
                style={{ padding: '12px 16px', borderRadius: 8, marginBottom: 8, cursor: sessResult ? 'default' : 'pointer', border: '1px solid ' + border, background: bg }}>
                {opt}
              </div>
            );
          })}
          {sessResult && (
            <div style={{ padding: '14px 18px', borderRadius: 8, marginTop: 12, background: sessResult.is_correct ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)', border: '1px solid ' + (sessResult.is_correct ? 'var(--accent-emerald)' : 'var(--accent-rose)') }}>
              <strong style={{ color: sessResult.is_correct ? '#6ee7b7' : '#fca5a5' }}>
                {sessResult.is_correct ? '✅ Right! Excellent mastery.' : '❌ Wrong answer.'}
              </strong>
              <span style={{ fontSize: 13, color: 'var(--text-secondary)', marginLeft: 10 }}>
                Mastery {sessResult.mastery_score}/100 · {sessResult.status}
              </span>
              {sessResult.xp_gained > 0 && <span className="badge badge-indigo" style={{ marginLeft: 10 }}>+{sessResult.xp_gained} XP</span>}
            </div>
          )}
          {sessResult && !sessResult.is_correct && sessRemediation && (
            <div className="glass-card" style={{ background: 'rgba(15, 23, 42, 0.9)', borderLeft: '4px solid var(--accent-amber)', marginTop: 14 }}>
              <h3 style={{ fontSize: 16, color: '#fcd34d', marginBottom: 10 }}>📚 Why it's wrong</h3>
              <div style={{ fontSize: 14, lineHeight: 1.6 }}>
                <div><strong style={{ color: '#fca5a5' }}>Why your choice doesn't fit:</strong> {sessRemediation.why_incorrect}</div>
                <div style={{ marginTop: 8 }}><strong style={{ color: '#6ee7b7' }}>Correct policy rationale:</strong> {sessRemediation.why_correct}</div>
                <div style={{ marginTop: 8, padding: '10px 14px', background: 'rgba(99, 102, 241, 0.1)', borderRadius: 8 }}>💡 <strong>Memory Hook:</strong> {sessRemediation.memory_hook}</div>
              </div>
              <button className="btn btn-secondary" style={{ marginTop: 12 }} onClick={explainSessionAgain} disabled={sessLoadingExplain}>
                {sessLoadingExplain ? <div className="spinner"></div> : '🤔 Still confused? Explain again (ELI5)'}
              </button>
              {sessExplainAgain && (
                <div style={{ marginTop: 12, padding: '12px 16px', background: 'rgba(245, 158, 11, 0.08)', borderRadius: 8, border: '1px solid rgba(245, 158, 11, 0.25)' }}>
                  <h4 style={{ fontSize: 14, color: '#fcd34d', marginBottom: 6 }}>💡 Simplified Analogy (ELI5):</h4>
                  <p style={{ fontSize: 14, lineHeight: 1.6 }}>{sessExplainAgain}</p>
                </div>
              )}
            </div>
          )}
          <div style={{ textAlign: 'right', marginTop: 12 }}>
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
        <div className="glass-card" style={{ padding: 32, marginBottom: 20, textAlign: 'center' }}>
          <h2>Session complete: {sessScore} / {session.questions.length} ({Math.round((sessScore / session.questions.length) * 100)}%)</h2>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', marginTop: 16 }}>
            <button className="btn btn-primary" onClick={startSession}>↻ New 20-question set</button>
          </div>
        </div>
      )}
    </div>
  );
}
