import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

// V2 practice: auto next-topic (weakness-weighted) + auto difficulty.
// Generation uses v1 generate_quiz_for_topic via /api/v2/quiz/generate (shape unchanged + personalization).
// Submit reuses v1 POST /api/quiz/submit (contract frozen).
export default function QuizPracticeV2({ selectedRole }) {
  const { user, refreshProfile } = useAuth();
  const [next, setNext] = useState(null);
  const [quiz, setQuiz] = useState(null);
  const [selected, setSelected] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleNext = async () => {
    setLoading(true);
    setQuiz(null);
    setSelected('');
    setResult(null);
    try {
      const nxt = await api.getQuizNext(user?.username || 'demo_user', selectedRole);
      setNext(nxt);
      const q = await api.generatePersonalizedQuiz(nxt.topic_id, selectedRole, user?.username || 'demo_user');
      setQuiz({ ...q, _topic: nxt.topic_id });
    } catch (err) {
      alert('V2 generate failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!selected || !quiz) return;
    try {
      const topicId = quiz._topic || 'company_basics';
      const res = await api.submitQuiz(user?.username || 'demo_user', topicId, selected, quiz.correct_answer);
      setResult(res);
      if (res.xp_gained > 0) refreshProfile();
    } catch (err) {
      alert('Submit failed: ' + err.message);
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
        <button className="btn btn-primary" onClick={handleNext} disabled={loading}>
          {loading ? 'Generating…' : '⚡ Next personalized question'}
        </button>
        {next && <span className="badge badge-indigo" style={{ marginLeft: 12 }}>{next.topic_id} · {next.difficulty} · {next.reason}</span>}
        {quiz?.personalization && <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>{quiz.personalization.reason}</div>}
      </div>
      {quiz && (
        <div className="glass-card" style={{ padding: 28 }}>
          <h2 style={{ marginBottom: 16 }}>{quiz.question}</h2>
          {quiz.options?.map((opt) => (
            <div key={opt} onClick={() => !result && setSelected(opt)}
              style={{ padding: '12px 16px', borderRadius: 8, marginBottom: 8, cursor: result ? 'default' : 'pointer', border: '1px solid ' + (selected === opt ? 'var(--primary)' : 'var(--border-subtle)'), background: selected === opt ? 'rgba(99,102,241,.2)' : 'rgba(15,23,42,.6)' }}>
              {opt}
            </div>
          ))}
          {!result
            ? <button className="btn btn-primary" style={{ marginTop: 12 }} onClick={handleSubmit} disabled={!selected}>Submit</button>
            : <div style={{ marginTop: 12 }}>
                <strong style={{ color: result.is_correct ? '#6ee7b7' : '#fca5a5' }}>{result.is_correct ? 'Correct' : 'Incorrect'}</strong>
                <span style={{ marginLeft: 12 }}>mastery {result.mastery_score} · {result.difficulty} · {result.status}</span>
                <div><button className="btn btn-primary" style={{ marginTop: 12 }} onClick={handleNext}>Next →</button></div>
              </div>}
        </div>
      )}
    </div>
  );
}
