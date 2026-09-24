import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function Login({ onAdmin }) {
  const { login, register, quickSwitchUser } = useAuth();
  const DEMO_ENABLED = import.meta.env.VITE_ENABLE_DEMO_LOGIN === 'true';
  const [isRegister, setIsRegister] = useState(false);
  
  const [username, setUsername] = useState('sarah_engineer');
  const [password, setPassword] = useState('password123');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('Software Engineer');
  const [department, setDepartment] = useState('Engineering');
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [demoUsers, setDemoUsers] = useState([]);

  useEffect(() => {
    if (!DEMO_ENABLED) return;
    api.getUsers().then(setDemoUsers).catch(console.error);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (isRegister && !DEMO_ENABLED) {
      setError('Self-registration disabled — contact admin');
      return;
    }
    setLoading(true);

    if (isRegister) {
      const res = await register({
        username,
        email,
        password,
        full_name: fullName,
        role,
        department
      });
      if (!res.success) setError(res.error);
    } else {
      const res = await login(username, password);
      if (!res.success) setError(res.error);
    }
    setLoading(false);
  };

  const handleQuickLogin = (userObj) => {
    quickSwitchUser(userObj);
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '24px',
      background: 'radial-gradient(ellipse at center, rgba(99, 102, 241, 0.15) 0%, #0b0f19 70%)'
    }}>
      <div style={{ width: '100%', maxWidth: '460px' }}>
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: '16px',
            background: 'var(--primary-gradient)',
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '28px',
            boxShadow: '0 8px 24px rgba(99, 102, 241, 0.45)',
            marginBottom: '16px'
          }}>
            🎓
          </div>
          <h1 style={{ fontSize: '30px', fontWeight: 800 }}>OnboardIQ</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
            Adaptive Corporate Onboarding & Knowledge Coach for <strong>Nexora</strong>
          </p>
        </div>

        {/* Main Card */}
        <div className="glass-card" style={{ padding: '32px' }}>
          <div style={{
            display: 'flex',
            borderBottom: '1px solid var(--border-subtle)',
            marginBottom: '24px',
            gap: '12px'
          }}>
            <button
              onClick={() => { setIsRegister(false); setError(''); }}
              style={{
                flex: 1,
                padding: '10px',
                background: 'none',
                border: 'none',
                borderBottom: !isRegister ? '2px solid var(--primary)' : '2px solid transparent',
                color: !isRegister ? '#ffffff' : 'var(--text-muted)',
                fontWeight: 700,
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              Sign In
            </button>
            {DEMO_ENABLED && (
            <button
              onClick={() => { setIsRegister(true); setError(''); }}
              style={{
                flex: 1,
                padding: '10px',
                background: 'none',
                border: 'none',
                borderBottom: isRegister ? '2px solid var(--primary)' : '2px solid transparent',
                color: isRegister ? '#ffffff' : 'var(--text-muted)',
                fontWeight: 700,
                fontSize: '14px',
                cursor: 'pointer'
              }}
            >
              Create Account
            </button>
            )}
          </div>

          {error && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              color: '#fca5a5',
              padding: '10px 14px',
              borderRadius: '8px',
              fontSize: '13px',
              marginBottom: '18px'
            }}>
              ⚠️ {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {isRegister && (
              <>
                <div className="input-group">
                  <label className="input-label">Full Name</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. Jordan Miller"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                  />
                </div>
                <div className="input-group">
                  <label className="input-label">Corporate Email</label>
                  <input
                    type="email"
                    required
                    className="form-input"
                    placeholder="name@nexora.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
                <div className="input-group">
                  <label className="input-label">Role</label>
                  <select
                    className="form-select"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                  >
                    <option value="Software Engineer">Software Engineer</option>
                    <option value="Product Manager">Product Manager</option>
                    <option value="DevOps Engineer">DevOps Engineer</option>
                    <option value="Sales Representative">Sales Representative</option>
                    <option value="Manager">Manager</option>
                    <option value="Admin">Administrator</option>
                  </select>
                </div>
              </>
            )}

            <div className="input-group">
              <label className="input-label">{isRegister ? 'Username' : 'Username or Email'}</label>
              <input
                type="text"
                required
                className="form-input"
                placeholder="sarah_engineer"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>

            <div className="input-group">
              <label className="input-label">Password</label>
              <input
                type="password"
                required
                className="form-input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', padding: '12px', fontSize: '15px', marginTop: '8px' }}
              disabled={loading}
            >
              {loading ? <div className="spinner"></div> : (isRegister ? 'Register & Begin Onboarding' : 'Sign In to Workspace')}
            </button>
          </form>

          {/* Quick Demo Logins — hidden unless demo flag enabled */}
          {DEMO_ENABLED && (
          <div style={{ marginTop: '28px', paddingTop: '20px', borderTop: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', display: 'block', marginBottom: '10px', textTransform: 'uppercase' }}>
              ⚡ Instant 1-Click Demo Profiles:
            </span>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
              {demoUsers.slice(0, 4).map(u => (
                <button
                  key={u.username}
                  type="button"
                  onClick={() => handleQuickLogin(u)}
                  className="btn btn-secondary"
                  style={{ padding: '8px 10px', fontSize: '12px', justifyContent: 'flex-start' }}
                >
                  👤 {u.full_name.split(' ')[0]} ({u.role.split(' ')[0]})
                </button>
              ))}
            </div>
          </div>
          )}
        </div>

        <div style={{ textAlign: 'center', marginTop: '20px', color: 'var(--text-muted)', fontSize: '12px' }}>
          Auth Data securely managed via dedicated <code>auth.db</code> isolated from vector indices.
        </div>
        {onAdmin && (
        <div style={{ textAlign: 'center', marginTop: 12 }}>
          <button onClick={onAdmin} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: 12, cursor: 'pointer', textDecoration: 'underline' }}>
            Admin sign-in →
          </button>
        </div>
        )}
      </div>
    </div>
  );
}
