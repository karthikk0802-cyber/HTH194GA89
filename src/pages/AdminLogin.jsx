import React, { useState } from 'react';
import { api } from '../services/api';

export default function AdminLogin({ onBack }) {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await api.adminLogin(username, password);
      localStorage.setItem('onboardiq_user', JSON.stringify(res.user));
      localStorage.setItem('onboardiq_token', res.token);
      window.location.reload();
    } catch (err) {
      setError(err.message || 'Admin login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="center" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div style={{ width: '100%', maxWidth: 400 }}>
        <div className="center" style={{ marginBottom: 28 }}>
          <h1 style={{ fontSize: 26 }}>OnboardIQ</h1>
          <p style={{ color: 'var(--muted)', fontSize: 13, marginTop: 4 }}>Administrator access</p>
        </div>
        <div className="card">
          <h3 style={{ fontSize: 16, marginBottom: 6 }}>Admin sign-in</h3>
          <p style={{ fontSize: 13, color: 'var(--muted)', marginBottom: 16 }}>
            Separate portal. Credentials come from server env (<code>ADMIN_USERNAME</code> / <code>ADMIN_PASSWORD</code>).
          </p>
          {error && <div className="notice notice-error">{error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label className="input-label">Admin username</label>
              <input className="form-input" value={username} onChange={(e) => setUsername(e.target.value)} required />
            </div>
            <div className="input-group">
              <label className="input-label">Admin password</label>
              <input className="form-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: 11 }} disabled={loading}>
              {loading ? <span className="spinner" /> : 'Sign in as admin'}
            </button>
          </form>
          {onBack && <button className="btn btn-secondary mt" style={{ width: '100%' }} onClick={onBack}>Back to user sign-in</button>}
        </div>
      </div>
    </div>
  );
}
