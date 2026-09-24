import React from 'react';
import './Sidebar.css';
import { useAuth } from '../context/AuthContext';

export default function Sidebar({ activeTab, setActiveTab }) {
  const { user, token } = useAuth();
  const isAdmin = !!user?.is_admin && (token || '').startsWith('admin_token_');

  const navigation = [
    { section: 'Learn' },
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'pre-assessment', label: 'Pre-Assessment' },
    { id: 'learning-path', label: 'Learning Roadmap' },
    { id: 'qa', label: 'Knowledge Coach' },
    { id: 'quiz', label: 'Practice Quizzes' },
    { id: 'scenarios', label: 'Applied Scenarios' },
    { id: 'voice-resources', label: 'Voice & Resources' },

    { section: 'Manage' },
    { id: 'manager', label: 'Team Readiness' },
    { id: 'admin', label: 'Knowledge Admin' },
    ...(isAdmin ? [{ id: 'admin-users', label: 'User Management' }] : [])
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        OnboardIQ<span className="brand-dot">.</span>
        <span className="sub">Nexora</span>
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
          return (
            <div
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              {item.label}
            </div>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <span>Adaptive engine</span>
        <span>v2.0</span>
      </div>
    </aside>
  );
}
