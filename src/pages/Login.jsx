import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export default function Login({ onAdmin }) {
  const { login, register, quickSwitchUser } = useAuth();
  const DEMO_ENABLED = import.meta.env.VITE_ENABLE_DEMO_LOGIN === 'true';
  const [isRegister, setIsRegister] = useState(false);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('Software Engineer');

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
        department: 'Engineering'
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
    <div className="center" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div style={{ width: '100%', maxWidth: 400 }}>
        <div className="center" style={{ marginBottom: 28 }}>
          <h1 style={{ fontSize: 26 }}>OnboardIQ</h1>
          <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 4 }}>
            Adaptive onboarding for Nexora
          </p>
        </div>

        <div className="card">
          {DEMO_ENABLED && (
            <div className="row" style={{ marginBottom: 20 }}>
              <button className={`btn btn-sm ${!isRegister ? 'btn-primary' : 'btn-secondary'}`} onClick={() => { setIsRegister(false); setError(''); }}>
                Sign In
              </button>
              <button className={`btn btn-sm ${isRegister ? 'btn-primary' : 'btn-secondary'}`} onClick={() => { setIsRegister(true); setError(''); }}>
                Create Account
              </button>
            </div>
          )}

          {!DEMO_ENABLED && (
            <h3 style={{ fontSize: 16, marginBottom: 16 }}>Sign in to your workspace</h3>
          )}

          {error && <div className="notice notice-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            {isRegister && (
              <>
                <div className="input-group">
                  <label className="input-label">Full Name</label>
                  <input type="text" required className="form-input" placeholder="Jordan Miller" value={fullName} onChange={(e) => setFullName(e.target.value)} />
                </div>
                <div className="input-group">
                  <label className="input-label">Corporate Email</label>
                  <input type="email" required className="form-input" placeholder="name@nexora.com" value={email} onChange={(e) => setEmail(e.target.value)} />
                </div>
                <div className="input-group">
                  <label className="input-label">Role</label>
                  <select className="form-select" value={role} onChange={(e) => setRole(e.target.value)}>
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
              <input type="text" required className="form-input" value={username} onChange={(e) => setUsername(e.target.value)} />
            </div>

            <div className="input-group">
              <label className="input-label">Password</label>
              <input type="password" required className="form-input" value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: 11 }} disabled={loading}>
              {loading ? <span className="spinner" /> : (isRegister ? 'Register & Begin' : 'Sign In')}
            </button>
          </form>

          {DEMO_ENABLED && demoUsers.length > 0 && (
            <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--line)' }}>
              <span className="kpi-label">Demo profiles</span>
              <div className="row mt">
                {demoUsers.slice(0, 4).map(u => (
                  <button key={u.username} type="button" onClick={() => handleQuickLogin(u)} className="btn btn-sm btn-secondary">
                    {u.full_name.split(' ')[0]} ({u.role.split(' ')[0]})
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {onAdmin && (
          <div className="center mt">
            <button onClick={onAdmin} style={{ background: 'none', border: 'none', fontSize: 12, cursor: 'pointer', color: 'var(--muted)', textDecoration: 'underline' }}>
              Admin sign-in
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
