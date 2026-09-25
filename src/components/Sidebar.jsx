import React from 'react';
import './Sidebar.css';

export default function Sidebar({ activeTab, setActiveTab, isAdmin, collapsed, onToggle }) {
  const learnerNav = [
    { section: 'Learn' },
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'pre-assessment', label: 'Pre-Assessment' },
    { id: 'learning-path', label: 'Learning Roadmap' },
    { id: 'qa', label: 'Knowledge Coach' },
    { id: 'quiz', label: 'Practice Quizzes' },
    { id: 'scenarios', label: 'Applied Scenarios' },
  ];

  const adminNav = [
    { section: 'Manage' },
    { id: 'admin-users', label: 'User Management' },
    { id: 'admin', label: 'Knowledge Admin' },
  ];

  const managerNav = [
    { section: 'Manage' },
    { id: 'manager', label: 'Team Readiness' },
    { id: 'admin', label: 'Knowledge Admin' },
  ];

  // Admins get the admin portal only — no learner content.
  const navigation = isAdmin ? adminNav : [...learnerNav, ...managerNav];

  return (
    <aside className={`sidebar${collapsed ? ' collapsed' : ''}`}>
      <div className="sidebar-brand">
        {!collapsed && (
          <>
            OnboardIQ<span className="brand-dot">.</span>
            <span className="sub">Nexora</span>
          </>
        )}
        {collapsed && <span>O<span className="brand-dot">.</span></span>}
        <button className="collapse-btn" onClick={onToggle} aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'} title={collapsed ? 'Expand' : 'Collapse'}>
          {collapsed ? '→' : '←'}
        </button>
      </div>

      <nav className="sidebar-nav">
        {navigation.map((item, idx) => {
          if (item.section) {
            return collapsed ? null : (
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
              title={item.label}
            >
              {collapsed ? item.label.charAt(0) : item.label}
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
