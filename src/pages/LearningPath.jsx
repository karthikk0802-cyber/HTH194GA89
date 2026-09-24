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
    return <span className="spinner spinner-lg" />;
  }

  return (
    <div>
      <div className="page-header">
        <h1><span className="kicker">01</span>Roadmap</h1>
        <p>{selectedRole} · ordered by prerequisites, not by guesswork.</p>
      </div>

      {pathData?.today_focus && (
        <div className="section">
          <div className="sec-head">
            <h3><span className="idx">02</span>Up next</h3>
            <button className="btn btn-sm btn-primary" onClick={() => handleStartPractice(pathData.today_focus.title || pathData.today_focus.topic_id)}>
              Practice →
            </button>
          </div>
          <p style={{ fontSize: '1.4rem', maxWidth: '30ch' }}>
            {pathData.today_focus.title || pathData.today_focus.topic_id.replace('_', ' ')}
          </p>
          <p className="sub">{pathData.today_focus.reason}</p>
        </div>
      )}

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">03</span>All competencies</h3>
        </div>
        <div>
          {pathData?.competencies?.map((comp) => {
            const isLocked = comp.status === 'Locked';
            return (
              <div key={comp.topic_id} className="dir-row">
                <div>
                  <div>
                    <div className="dir-main">{comp.title}</div>
                    <div className="dir-sub">
                      {comp.prerequisites.length > 0 ? `Requires ${comp.prerequisites.join(', ')}` : 'Foundation'} · {comp.difficulty} · {comp.status} · {comp.mastery_score}/100
                    </div>
                  </div>
                  <button
                    className="btn btn-sm btn-secondary"
                    disabled={isLocked}
                    onClick={() => handleStartPractice(comp.title)}
                  >
                    {isLocked ? 'Locked' : comp.status === 'Completed' ? 'Review →' : 'Practice →'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">04</span>Dependencies</h3>
          <span className="note">prerequisite graph</span>
        </div>
        <p className="mono" style={{ fontSize: 13, lineHeight: 2.1 }}>
          {pathData?.graph_edges?.map((edge, i) => (
            <span key={i}>
              {edge.source_title} <span style={{ color: 'var(--accent)' }}>→</span> {edge.target_title}
              {i < pathData.graph_edges.length - 1 ? <><br /></> : null}
            </span>
          ))}
        </p>
      </div>
    </div>
  );
}
