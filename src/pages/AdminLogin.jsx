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
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div style={{ width: '100%', maxWidth: 420 }}>
        <div className="glass-card" style={{ padding: 32 }}>
          <h1 style={{ fontSize: 22, marginBottom: 4 }}>Admin sign-in</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 20 }}>
            Separate portal. Credentials come from server env (<code>ADMIN_USERNAME</code> / <code>ADMIN_PASSWORD</code>).
          </p>
          {error && <div style={{ background: 'rgba(239,68,68,.15)', border: '1px solid rgba(239,68,68,.3)', color: '#fca5a5', padding: '10px 14px', borderRadius: 8, fontSize: 13, marginBottom: 16 }}>⚠️ {error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="input-group">
              <label className="input-label">Admin username</label>
              <input className="form-input" value={username} onChange={(e) => setUsername(e.target.value)} required />
            </div>
            <div className="input-group">
              <label className="input-label">Admin password</label>
              <input className="form-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required placeholder="••••••••" />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: 12 }} disabled={loading}>
              {loading ? <div className="spinner" /> : 'Sign in as admin'}
            </button>
          </form>
          {onBack && <button className="btn btn-secondary" style={{ width: '100%', marginTop: 12 }} onClick={onBack}>← Back to user sign-in</button>}
        </div>
      </div>
    </div>
  );
}
