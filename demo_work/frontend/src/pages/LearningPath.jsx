import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function LearningPath({ selectedRole, setActiveTab, setSelectedQuizTopic }) {
  const { user } = useAuth();
  const [pathData, setPathData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    api.getLearningPath(user.username, selectedRole)
      .then(setPathData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [user, selectedRole]);

  const handleStartPractice = (topicTitle) => {
    if (setSelectedQuizTopic) {
      setSelectedQuizTopic(topicTitle);
    }
    setActiveTab('quiz');
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
          <h1>Adaptive Learning Roadmap</h1>
          <p>Deterministic competency progression for <strong>{selectedRole}</strong> powered by prerequisite DAGs.</p>
        </div>
      </div>

      {/* Hero Focus Topic */}
      {pathData?.today_focus && (
        <div className="glass-card" style={{ marginBottom: '28px', borderLeft: '4px solid var(--primary)', background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(17, 24, 39, 0.8) 100%)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <span className="badge badge-indigo" style={{ marginBottom: '8px' }}>TOP PRIORITY MODULE</span>
              <h2 style={{ fontSize: '24px', marginTop: '6px' }}>
                {pathData.today_focus.title || pathData.today_focus.topic_id.replace('_', ' ').toUpperCase()}
              </h2>
              <p style={{ color: 'var(--text-secondary)', marginTop: '8px', fontSize: '14px', maxWidth: '750px' }}>
                💡 <strong>Why this topic now?</strong> {pathData.today_focus.reason}
              </p>
            </div>
            <button
              className="btn btn-primary"
              style={{ padding: '12px 24px', fontSize: '15px' }}
              onClick={() => handleStartPractice(pathData.today_focus.title || pathData.today_focus.topic_id)}
            >
              Start Module Practice →
            </button>
          </div>
        </div>
      )}

      {/* Competencies Grid */}
      <h3 style={{ fontSize: '20px', marginBottom: '16px' }}>All Role Competencies</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        {pathData?.competencies?.map((comp) => {
          const isCompleted = comp.status === 'Completed';
          const isCurrent = comp.status === 'Current';
          const isLocked = comp.status === 'Locked';

          return (
            <div
              key={comp.topic_id}
              className={`glass-card ${!isLocked ? 'interactive' : ''}`}
              style={{
                opacity: isLocked ? 0.65 : 1,
                border: isCurrent ? '1px solid var(--border-active)' : '1px solid var(--border-subtle)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '14px' }}>
                <div>
                  <h4 style={{ fontSize: '17px', color: '#ffffff' }}>{comp.title}</h4>
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {comp.prerequisites.length > 0 ? `Requires: ${comp.prerequisites.join(', ')}` : 'No Prerequisites (Foundation)'}
                  </span>
                </div>
                <span className={`badge ${
                  isCompleted ? 'badge-emerald' :
                  isCurrent ? 'badge-indigo' :
                  comp.status === 'Needs-Review' ? 'badge-amber' : 'badge-gray'
                }`}>
                  {comp.status}
                </span>
              </div>

              {/* Progress Bar */}
              <div style={{ marginBottom: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Mastery: {comp.difficulty}</span>
                  <span style={{ fontWeight: 700 }}>{comp.mastery_score} / 100</span>
                </div>
                <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '999px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${comp.mastery_score}%`,
                    height: '100%',
                    background: comp.mastery_score >= 80 ? 'linear-gradient(90deg, #10b981, #059669)' :
                                comp.mastery_score >= 50 ? 'linear-gradient(90deg, #6366f1, #8b5cf6)' :
                                'linear-gradient(90deg, #f59e0b, #d97706)',
                    borderRadius: '999px',
                    transition: 'width 0.5s ease'
                  }}></div>
                </div>
              </div>

              {/* Action Button */}
              <button
                className={`btn ${isLocked ? 'btn-secondary' : 'btn-primary'}`}
                style={{ width: '100%', padding: '8px', fontSize: '13px' }}
                disabled={isLocked}
                onClick={() => handleStartPractice(comp.title)}
              >
                {isLocked ? '🔒 Prerequisites Incomplete' : (isCompleted ? '🔄 Spaced Review Practice' : '⚡ Launch Quiz Practice')}
              </button>
            </div>
          );
        })}
      </div>

      {/* NetworkX Prerequisite Dependency Flow */}
      <div className="glass-card">
        <h3 style={{ fontSize: '18px', marginBottom: '12px' }}>Deterministic Competency Dependency Flow</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '16px' }}>
          Prerequisite relations enforced by the NetworkX DAG engine:
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
          {pathData?.graph_edges?.map((edge, i) => (
            <div
              key={i}
              style={{
                padding: '8px 14px',
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                fontSize: '13px'
              }}
            >
              <span style={{ color: '#a5b4fc', fontWeight: 600 }}>{edge.source_title}</span>
              <span style={{ color: 'var(--text-muted)' }}>➔</span>
              <span style={{ color: '#6ee7b7', fontWeight: 600 }}>{edge.target_title}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
