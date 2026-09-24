import React from 'react';
import './Sidebar.css';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ activeTab, setActiveTab }) {
  const { user, token } = useAuth();
  const isAdmin = !!user?.is_admin && (token || '').startsWith('admin_token_');

  const navigation = [
    { section: 'Learner Workspace' },
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'pre-assessment', label: 'Pre-Assessment', icon: '📝' },
    { id: 'learning-path', label: 'Learning Roadmap', icon: '🗺️' },
    { id: 'qa', label: 'Knowledge Coach', icon: '💡' },
    { id: 'quiz', label: 'Adaptive Quizzes', icon: '🎯' },
    { id: 'scenarios', label: 'Applied Scenarios', icon: '🧩' },
    { id: 'voice-resources', label: 'Voice & Resources', icon: '🎙️' },

    { section: 'Management & Oversight' },
    { id: 'manager', label: 'Team Readiness', icon: '👥' },
    { id: 'admin', label: 'Knowledge Admin', icon: '⚙️' },
    ...(isAdmin ? [{ id: 'admin-users', label: 'User Management', icon: '🔐' }] : [])
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">🎓</div>
        <div className="brand-info">
          <h2>OnboardIQ</h2>
          <span>Nexora Enterprise</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navigation.map((item, idx) => {
          if (item.section) {
            return (
              <div key={idx} className="nav-section-title">
                {item.section}
              </div>
            );
          }

          const isActive = activeTab === item.id;
          return (
            <div
              key={item.id}
              className={`nav-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </div>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="footer-system-status">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div className="pulse-dot"></div>
            <span>Adaptive Engine Online</span>
          </div>
          <span className="badge badge-indigo" style={{ padding: '2px 6px', fontSize: '10px' }}>v2.0</span>
        </div>
      </div>
    </aside>
  );
}
