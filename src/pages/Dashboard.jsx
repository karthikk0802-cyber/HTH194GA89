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
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <div className="spinner" style={{ width: '36px', height: '36px' }}></div>
      </div>
    );
  }

  const xpCurrent = stats?.xp || 0;
  const nextLevelXp = stats?.xp_next_level || 100;
  const xpProgress = Math.min(100, Math.round(((xpCurrent % 100) / 100) * 100));

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Welcome back, {user?.full_name || 'Learner'} 👋</h1>
          <p>Role Roadmap: <strong>{selectedRole}</strong> • Track your adaptive learning milestones</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setActiveTab('quiz')}
        >
          ⚡ Start Today's Practice
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid-4" style={{ marginBottom: '28px' }}>
        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>CURRENT LEVEL</span>
            <span style={{ fontSize: '20px' }}>⭐</span>
          </div>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#ffffff' }}>
            Level {stats?.level || 1}
          </div>
          <div style={{ marginTop: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
              <span>Progress to Lvl {(stats?.level || 1) + 1}</span>
              <span>{xpCurrent % 100} / 100 XP</span>
            </div>
            <div style={{ width: '100%', height: '6px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '999px', overflow: 'hidden' }}>
              <div style={{ width: `${xpProgress}%`, height: '100%', background: 'var(--primary-gradient)', borderRadius: '999px', transition: 'width 0.5s ease' }}></div>
            </div>
          </div>
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>TOTAL XP</span>
            <span style={{ fontSize: '20px' }}>⚡</span>
          </div>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#818cf8' }}>
            {stats?.xp || 0} <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-muted)' }}>XP</span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>
            +{stats?.mastered_count * 50 || 0} XP earned this week
          </p>
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>ACTIVE STREAK</span>
            <span style={{ fontSize: '20px' }}>🔥</span>
          </div>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#fb923c' }}>
            {stats?.streak_days || 1} <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-muted)' }}>Days</span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>
            Keep logging in daily to protect your streak!
          </p>
        </div>

        <div className="glass-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>ROLE READINESS</span>
            <span style={{ fontSize: '20px' }}>🎯</span>
          </div>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#34d399' }}>
            {stats?.readiness_percentage || 0}%
          </div>
          <div style={{ marginTop: '10px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '4px' }}>
              <span>{stats?.mastered_count || 0} of {stats?.total_topics || 0} Mastered</span>
              <span>Expert Tier</span>
            </div>
            <div style={{ width: '100%', height: '6px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '999px', overflow: 'hidden' }}>
              <div style={{ width: `${stats?.readiness_percentage || 0}%`, height: '100%', background: 'linear-gradient(90deg, #10b981, #06b6d4)', borderRadius: '999px' }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid Section */}
      <div className="grid-2" style={{ marginBottom: '28px' }}>
        {/* Left Column: Today's Focus & Competencies */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Today's Focus Hero Card */}
          <div className="glass-card interactive" style={{ borderLeft: '4px solid var(--primary)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
              <div>
                <span className="badge badge-indigo">TODAY'S ADAPTIVE FOCUS</span>
                <h3 style={{ fontSize: '20px', marginTop: '8px' }}>
                  {learningPath?.today_focus ? learningPath.today_focus.title || learningPath.today_focus.topic_id.replace('_', ' ').toUpperCase() : 'All Modules In Progress'}
                </h3>
              </div>
              <button
                className="btn btn-primary"
                onClick={() => setActiveTab('quiz')}
              >
                Launch Module →
              </button>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              <strong>Why am I learning this next?</strong> {learningPath?.today_focus?.reason || 'Based on your prerequisite graph, this topic unlocks next-level architecture standards.'}
            </p>
          </div>

          {/* Competency Mastery List */}
          <div className="glass-card">
            <h3 style={{ fontSize: '18px', marginBottom: '18px' }}>Competency Matrix ({selectedRole})</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {learningPath?.competencies?.map(comp => (
                <div key={comp.topic_id}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '14px', fontWeight: 600 }}>{comp.title}</span>
                      <span className={`badge ${
                        comp.status === 'Completed' ? 'badge-emerald' :
                        comp.status === 'Current' ? 'badge-indigo' :
                        comp.status === 'Needs-Review' ? 'badge-amber' : 'badge-gray'
                      }`}>
                        {comp.difficulty} • {comp.status}
                      </span>
                    </div>
                    <span style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {comp.mastery_score} / 100
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '8px', background: 'rgba(255, 255, 255, 0.06)', borderRadius: '999px', overflow: 'hidden' }}>
                    <div style={{
                      width: `${comp.mastery_score}%`,
                      height: '100%',
                      background: comp.mastery_score >= 80 ? 'linear-gradient(90deg, #10b981, #059669)' :
                                  comp.mastery_score >= 50 ? 'linear-gradient(90deg, #6366f1, #8b5cf6)' :
                                  'linear-gradient(90deg, #f59e0b, #d97706)',
                      borderRadius: '999px',
                      transition: 'width 0.6s ease'
                    }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Achievements & Weak Areas */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Achievement Badges */}
          <div className="glass-card">
            <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Unlocked Achievements</h3>
            {stats?.badges && stats.badges.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                {stats.badges.map((b, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '12px 14px',
                      background: 'rgba(99, 102, 241, 0.1)',
                      border: '1px solid rgba(99, 102, 241, 0.3)',
                      borderRadius: 'var(--radius-md)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px'
                    }}
                  >
                    <span style={{ fontSize: '24px' }}>🏆</span>
                    <div>
                      <div style={{ fontSize: '13px', fontWeight: 700, color: '#ffffff' }}>{b}</div>
                      <div style={{ fontSize: '11px', color: '#a5b4fc' }}>Unlocked Achievement</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px', border: '1px dashed var(--border-subtle)', borderRadius: 'var(--radius-md)' }}>
                Complete quizzes with &gt;80% score or maintain a 7-day streak to unlock badges!
              </div>
            )}
          </div>

          {/* Weak Areas Alert Card */}
          <div className="glass-card">
            <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Attention Areas & Spaced Reviews</h3>
            {stats?.weak_areas && stats.weak_areas.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {stats.weak_areas.map(area => (
                  <div
                    key={area.topic_id}
                    style={{
                      padding: '12px 16px',
                      background: 'rgba(245, 158, 11, 0.08)',
                      border: '1px solid rgba(245, 158, 11, 0.25)',
                      borderRadius: 'var(--radius-md)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '14px', fontWeight: 600, color: '#fcd34d' }}>⚠️ {area.title}</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Mastery score: {area.mastery}/100</div>
                    </div>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '6px 12px', fontSize: '12px' }}
                      onClick={() => setActiveTab('quiz')}
                    >
                      Review Now
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ padding: '20px', textAlign: 'center', color: '#6ee7b7', background: 'rgba(16, 185, 129, 0.06)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                ✨ Great work! No weak topics or overdue spaced repetition reviews.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
