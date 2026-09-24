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

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Applied Scenario Training</h1>
          <p>Test your real-world judgment against critical incidents graded across a 4-pillar evaluation rubric.</p>
        </div>
      </div>

      {/* Scenario Selector & Situation */}
      <div className="glass-card" style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', flexWrap: 'wrap' }}>
          {scenarios.map(s => (
            <button
              key={s.id}
              className={`btn ${selectedScenarioId === s.id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => { setSelectedScenarioId(s.id); setEvalResult(null); setUserResponse(''); }}
            >
              🧩 {s.title}
            </button>
          ))}
        </div>

        {activeScenario && (
          <div style={{
            padding: '24px',
            background: 'rgba(99, 102, 241, 0.08)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            borderRadius: 'var(--radius-lg)',
            marginBottom: '24px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
              <span className="badge badge-indigo">CRITICAL INCIDENT BRIEFING</span>
              <span className="badge badge-cyan">{activeScenario.topic_id.replace('_', ' ').toUpperCase()}</span>
            </div>
            <h3 style={{ fontSize: '18px', color: '#ffffff', marginBottom: '10px' }}>{activeScenario.title}</h3>
            <p style={{ fontSize: '15px', color: '#f3f4f6', lineHeight: 1.6 }}>
              {activeScenario.text}
            </p>
          </div>
        )}

        {/* User Response Form */}
        <form onSubmit={handleEvaluate}>
          <div className="input-group">
            <label className="input-label">Your Proposed Action Plan & Step-by-Step Response:</label>
            <textarea
              className="form-textarea"
              style={{ minHeight: '130px', fontSize: '14px', lineHeight: 1.6 }}
              placeholder="Walk through your immediate containment steps, communication channels, and procedures according to Nexora policy..."
              value={userResponse}
              onChange={(e) => setUserResponse(e.target.value)}
            ></textarea>
          </div>

          <div style={{ textAlign: 'right' }}>
            <button
              type="submit"
              className="btn btn-primary"
              style={{ padding: '12px 32px', fontSize: '15px' }}
              disabled={loading || !userResponse.trim()}
            >
              {loading ? <div className="spinner"></div> : '⚡ Evaluate Across 4-Pillar Rubric'}
            </button>
          </div>
        </form>
      </div>

      {/* Evaluation Result View */}
      {evalResult && (
        <div className="glass-card" style={{ marginBottom: '28px', borderLeft: '4px solid var(--accent-emerald)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '24px' }}>🏆</span>
              <h3 style={{ fontSize: '18px' }}>4-Pillar Evaluation Scorecard</h3>
            </div>
            {evalResult.xp_gained > 0 && (
              <span className="badge badge-emerald" style={{ fontSize: '14px', padding: '6px 14px' }}>
                +{evalResult.xp_gained} XP Awarded! ⚡
              </span>
            )}
          </div>

          {/* 4 Pillars Grid */}
          <div className="grid-4" style={{ marginBottom: '24px' }}>
            <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.7)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>POLICY KNOWLEDGE</span>
              <div style={{ fontSize: '28px', fontWeight: 800, color: '#818cf8', marginTop: '6px' }}>
                {evalResult.policy_score || 0} <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>/10</span>
              </div>
            </div>

            <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.7)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>DECISION QUALITY</span>
              <div style={{ fontSize: '28px', fontWeight: 800, color: '#34d399', marginTop: '6px' }}>
                {evalResult.decision_score || 0} <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>/10</span>
              </div>
            </div>

            <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.7)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>PROCEDURE ADHERENCE</span>
              <div style={{ fontSize: '28px', fontWeight: 800, color: '#67e8f9', marginTop: '6px' }}>
                {evalResult.procedure_score || 0} <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>/10</span>
              </div>
            </div>

            <div style={{ padding: '16px', background: 'rgba(15, 23, 42, 0.7)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', textAlign: 'center' }}>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>RISK AWARENESS</span>
              <div style={{ fontSize: '28px', fontWeight: 800, color: '#fcd34d', marginTop: '6px' }}>
                {evalResult.risk_score || 0} <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>/10</span>
              </div>
            </div>
          </div>

          {/* Feedback */}
          <div style={{ padding: '18px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            <h4 style={{ fontSize: '14px', color: '#ffffff', marginBottom: '6px' }}>Evaluator Feedback:</h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', lineHeight: 1.6 }}>
              {evalResult.feedback}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
