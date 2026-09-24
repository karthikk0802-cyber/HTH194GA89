import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function AppliedScenarios() {
  const { user } = useAuth();
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenarioId, setSelectedScenarioId] = useState('');
  const [userResponse, setUserResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [evalResult, setEvalResult] = useState(null);

  useEffect(() => {
    api.getScenarios().then(data => {
      setScenarios(data);
      if (data.length > 0) setSelectedScenarioId(data[0].id);
    }).catch(console.error);
  }, []);

  const activeScenario = scenarios.find(s => s.id === selectedScenarioId) || scenarios[0];

  const handleEvaluate = async (e) => {
    e.preventDefault();
    if (!userResponse.trim()) return;

    setLoading(true);
    setEvalResult(null);
    try {
      const res = await api.evaluateScenario(user?.username || 'demo_user', selectedScenarioId, userResponse);
      setEvalResult(res);
    } catch (err) {
      alert('Scenario evaluation failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const pillars = evalResult ? [
    ['Policy knowledge', evalResult.policy_score],
    ['Decision quality', evalResult.decision_score],
    ['Procedure adherence', evalResult.procedure_score],
    ['Risk awareness', evalResult.risk_score],
  ] : [];

  return (
    <div>
      <div className="page-header">
        <h1><span className="kicker">01</span>Scenarios</h1>
        <p>Real incidents. Your judgment, graded on four pillars.</p>
      </div>

      <div className="section">
        <div className="row">
          {scenarios.map(s => (
            <button
              key={s.id}
              className={`btn btn-sm ${selectedScenarioId === s.id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => { setSelectedScenarioId(s.id); setEvalResult(null); setUserResponse(''); }}
            >
              {s.title}
            </button>
          ))}
        </div>
      </div>

      {activeScenario && (
        <div className="section">
          <div className="sec-head">
            <h3><span className="idx">02</span>{activeScenario.title}</h3>
            <span className="badge badge-indigo">{activeScenario.topic_id.replace('_', ' ')}</span>
          </div>
          <p style={{ fontSize: '1.15rem', maxWidth: '68ch' }}>{activeScenario.text}</p>

          <form onSubmit={handleEvaluate} className="mt">
            <div className="input-group">
              <label className="input-label">Your action plan, step by step</label>
              <textarea
                className="form-textarea"
                placeholder="Containment steps, channels, procedures per Nexora policy…"
                value={userResponse}
                onChange={(e) => setUserResponse(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading || !userResponse.trim()}>
              {loading ? <span className="spinner" /> : 'Evaluate response'}
            </button>
          </form>
        </div>
      )}

      {evalResult && (
        <div className="section">
          <div className="sec-head">
            <h3><span className="idx">03</span>Scorecard</h3>
            {evalResult.xp_gained > 0 && <span className="note">+{evalResult.xp_gained} XP</span>}
          </div>
          <div className="row" style={{ gap: 40 }}>
            {pillars.map(([label, score]) => (
              <div key={label}>
                <div className="kpi-label">{label}</div>
                <div className="kpi">{score || 0}<span style={{ fontSize: '1rem', color: 'var(--muted)' }}>/10</span></div>
              </div>
            ))}
          </div>
          <p className="mt" style={{ maxWidth: '68ch' }}>{evalResult.feedback}</p>
        </div>
      )}
    </div>
  );
}
