import React, { useState, useEffect } from 'react';
import './Navbar.css';
import { useAuth } from '../context/AuthContext';
import ChangePassword from './ChangePassword';

export default function Navbar({ activeTab, selectedRole }) {
  const { user, profileStats, logout } = useAuth();
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [theme, setTheme] = useState(
    () => localStorage.getItem('onboardiq_theme') || 'dark'
  );

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('onboardiq_theme', theme);
  }, [theme]);

  const titlesMap = {
    'dashboard': 'Dashboard',
    'pre-assessment': 'Pre-Assessment',
    'learning-path': 'Learning Roadmap',
    'qa': 'Knowledge Coach',
    'quiz': 'Practice Quizzes',
    'scenarios': 'Applied Scenarios',
    'voice-resources': 'Voice & Resources',
    'manager': 'Team Readiness',
    'admin': 'Knowledge Admin',
    'admin-users': 'User Management'
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <header className="navbar">
      <div className="navbar-left">
        <div className="breadcrumb">
          <span>Nexora</span>
          <span>/</span>
          <span className="current">{titlesMap[activeTab] || 'Workspace'}</span>
        </div>
      </div>

      <div className="navbar-right">
        <span className="badge badge-indigo">{user?.role || selectedRole}</span>

        {user && (
          <>
            <span className="stat-pill"><strong>{profileStats?.xp || 0}</strong>&nbsp;XP · Lv&nbsp;{profileStats?.level || 1}</span>
            <div className="user-profile-menu">
              <div className="user-avatar">{getInitials(user.full_name)}</div>
              <div className="user-meta">
                <span className="name">{user.full_name}</span>
                <span className="dept">{user.department}</span>
              </div>
              <button className="btn btn-sm btn-secondary" onClick={() => setShowPasswordModal(true)}>
                Password
              </button>
              <button className="btn btn-sm btn-secondary" onClick={logout}>
                Sign out
              </button>
            </div>
          </>
        )}

        <button
          className="theme-btn"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          aria-label="Toggle theme"
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
        >
          {theme === 'dark' ? '○' : '●'}
        </button>

        {showPasswordModal && <ChangePassword onDone={() => setShowPasswordModal(false)} />}
      </div>
    </header>
  );
}
