import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function Dashboard({ selectedRole, setActiveTab }) {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [learningPath, setLearningPath] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    Promise.all([
      api.getDashboardSummary(user.username, selectedRole),
      api.getLearningPath(user.username, selectedRole)
    ])
      .then(([dashData, pathData]) => {
        setStats(dashData);
        setLearningPath(pathData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [user, selectedRole]);

  if (loading) {
    return <span className="spinner spinner-lg" />;
  }

  const focus = learningPath?.today_focus;

  return (
    <div>
      <div className="page-header">
        <h1><span className="kicker">01</span>Welcome back, {user?.full_name?.split(' ')[0] || 'Learner'}</h1>
        <p>{selectedRole} roadmap · {stats?.mastered_count || 0} of {stats?.total_topics || 0} topics mastered</p>
      </div>

      <div className="section">
        <div className="row" style={{ gap: 48 }}>
          <div>
            <div className="kpi-label">Level</div>
            <div className="kpi">{stats?.level || 1}</div>
            <div className="cell-sub">{xpRemainder(stats)} / 100 XP to next</div>
          </div>
          <div>
            <div className="kpi-label">Total XP</div>
            <div className="kpi">{stats?.xp || 0}</div>
            <div className="cell-sub">Streak {stats?.streak_days || 1} day{(stats?.streak_days || 1) === 1 ? '' : 's'}</div>
          </div>
          <div>
            <div className="kpi-label">Readiness</div>
            <div className="kpi">{stats?.readiness_percentage || 0}%</div>
            <div className="cell-sub">Expert tier target</div>
          </div>
        </div>
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">02</span>Today's focus</h3>
          <button className="btn btn-sm btn-primary" onClick={() => setActiveTab('quiz')}>
            Practice →
          </button>
        </div>
        {focus ? (
          <>
            <p style={{ fontSize: '1.25rem', maxWidth: '34ch' }}>
              {focus.title || focus.topic_id.replace('_', ' ')}
            </p>
            <p className="sub">{focus.reason}</p>
          </>
        ) : (
          <p className="sub">All modules in progress. Open practice to continue.</p>
        )}
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">03</span>Competencies</h3>
          <span className="note">{selectedRole}</span>
        </div>
        <div>
          {learningPath?.competencies?.map(comp => (
            <div key={comp.topic_id} className="dir-row">
              <div>
                <div>
                  <div className="dir-main">{comp.title}</div>
                  <div className="dir-sub">{comp.difficulty} · {comp.status} · {comp.mastery_score}/100</div>
                </div>
                <span className="badge badge-gray">{comp.mastery_score}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">04</span>Achievements</h3>
        </div>
        {stats?.badges && stats.badges.length > 0 ? (
          <div>
            {stats.badges.map((b, i) => (
              <div key={i} className="dir-row">
                <div>
                  <div className="dir-main">{b}</div>
                  <div className="dir-sub">Unlocked</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="sub">Complete quizzes above 80% or hold a 7-day streak to unlock badges.</p>
        )}
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">05</span>Needs attention</h3>
        </div>
        {stats?.weak_areas && stats.weak_areas.length > 0 ? (
          <div>
            {stats.weak_areas.map(area => (
              <div key={area.topic_id} className="dir-row">
                <div>
                  <div>
                    <div className="dir-main">{area.title}</div>
                    <div className="dir-sub">Mastery {area.mastery}/100</div>
                  </div>
                  <button className="btn btn-sm btn-secondary" onClick={() => setActiveTab('quiz')}>
                    Review →
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="sub">Nothing weak, nothing overdue. Good standing.</p>
        )}
      </div>
    </div>
  );
}

function xpRemainder(stats) {
  const xp = stats?.xp || 0;
  return xp % 100;
}
