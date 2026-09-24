import React, { useState, useEffect } from 'react';
import './Navbar.css';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function Navbar({ activeTab, selectedRole, setSelectedRole }) {
  const { user, profileStats, logout, quickSwitchUser } = useAuth();
  const [allUsers, setAllUsers] = useState([]);
  const [showSwitchModal, setShowSwitchModal] = useState(false);

  useEffect(() => {
    api.getUsers().then(setAllUsers).catch(console.error);
  }, []);


  const titlesMap = {
    'dashboard': 'Employee Overview & Progress',
    'pre-assessment': 'Diagnostic Pre-Assessment & Bypass',
    'learning-path': 'Adaptive Learning Roadmap & Competency Graph',
    'qa': 'AI Knowledge Coach (Grounded RAG)',
    'quiz': 'Dynamic Practice Quizzes & Remediation',
    'scenarios': 'Applied Critical Scenario Training',
    'voice-resources': 'Voice Tutor & Curated Intranet Library',
    'manager': 'Manager Team Readiness & Compliance Matrix',
    'admin': 'Knowledge Base & Audit Administration'
  };

  const rolesList = [
    'Software Engineer',
    'Product Manager',
    'DevOps Engineer',
    'Sales Representative',
    'Marketing Specialist',
    'HR Manager',
    'Data Scientist',
    'Customer Support'
  ];

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
        {/* Role Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 600 }}>ROLE VIEW:</span>
          <select
            className="role-switcher-select"
            value={selectedRole}
            onChange={(e) => setSelectedRole(e.target.value)}
          >
            {rolesList.map(r => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>

        {/* Live XP & Level Badges */}
        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              background: 'rgba(99, 102, 241, 0.15)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: 700,
              color: '#a5b4fc'
            }}>
              <span>⚡</span>
              <span>{profileStats?.xp || 0} XP</span>
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '6px 10px',
              background: 'rgba(16, 185, 129, 0.15)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: 700,
              color: '#6ee7b7'
            }}>
              <span>⭐</span>
              <span>Lvl {profileStats?.level || 1}</span>
            </div>
          </div>
        )}


        {/* User Pill */}
        {user && (
          <div className="user-profile-menu">
            <div className="user-avatar">{getInitials(user.full_name)}</div>
            <div className="user-meta">
              <span className="name">{user.full_name}</span>
              <span className="dept">{user.department} • {user.role}</span>
            </div>
            <button
              className="btn btn-secondary"
              style={{ padding: '4px 8px', fontSize: '11px', borderRadius: '6px' }}
              onClick={() => setShowSwitchModal(!showSwitchModal)}
              title="Switch user account"
            >
              Switch ▾
            </button>
            <button
              className="btn btn-danger"
              style={{ padding: '4px 8px', fontSize: '11px', borderRadius: '6px' }}
              onClick={logout}
              title="Sign out"
            >
              Logout
            </button>
          </div>
        )}

        {/* Quick Switch Dropdown */}
        {showSwitchModal && (
          <div
            style={{
              position: 'absolute',
              top: '75px',
              right: '32px',
              width: '320px',
              background: 'rgba(17, 24, 39, 0.98)',
              border: '1px solid var(--border-active)',
              borderRadius: 'var(--radius-lg)',
              boxShadow: 'var(--shadow-lg)',
              padding: '16px',
              zIndex: 200,
              backdropFilter: 'blur(20px)'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h4 style={{ fontSize: '14px', fontWeight: 700 }}>Switch Active Account</h4>
              <button
                style={{ background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer' }}
                onClick={() => setShowSwitchModal(false)}
              >
                ✕
              </button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '260px', overflowY: 'auto' }}>
              {allUsers.map(u => (
                <div
                  key={u.username}
                  onClick={() => {
                    quickSwitchUser(u);
                    setSelectedRole(u.role || 'Software Engineer');
                    setShowSwitchModal(false);
                  }}
                  style={{
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-md)',
                    background: u.username === user?.username ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid ' + (u.username === user?.username ? 'var(--border-active)' : 'transparent'),
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div>
                    <div style={{ fontSize: '13px', fontWeight: 600 }}>{u.full_name}</div>
                    <div style={{ fontSize: '11px', color: '#9ca3af' }}>{u.department} • {u.role}</div>
                  </div>
                  {u.is_admin && <span className="badge badge-amber" style={{ fontSize: '10px' }}>Admin</span>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
