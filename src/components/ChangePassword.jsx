import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export default function ChangePassword({ forced = false, onDone }) {
  const { user, changePassword, logout } = useAuth();
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (newPassword.length < 8) {
      setError('New password must be at least 8 characters');
      return;
    }
    if (newPassword !== confirm) {
      setError('New passwords do not match');
      return;
    }
    setSaving(true);
    const res = await changePassword(user?.username, oldPassword, newPassword);
    setSaving(false);
    if (!res.success) {
      setError(res.error);
      return;
    }
    if (onDone) onDone();
  };

  return (
    <div style={{
      position: forced ? 'fixed' : 'static',
      top: 0, left: 0, right: 0, bottom: 0,
      background: forced ? 'rgba(0,0,0,0.8)' : 'transparent',
      backdropFilter: forced ? 'blur(8px)' : 'none',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 1000, padding: 20
    }}>
      <div className="glass-card" style={{ width: '100%', maxWidth: 440, padding: 28 }}>
        <h3 style={{ fontSize: 18, marginBottom: 6 }}>
          {forced ? 'Set your password to continue' : 'Change password'}
        </h3>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16 }}>
          {forced
            ? 'Your account still uses the default first-login password. Choose a personal password.'
            : 'Enter your current password, then choose a new one (min 8 characters).'}
        </p>
        {error && <div style={{ background: 'rgba(239,68,68,.15)', border: '1px solid rgba(239,68,68,.3)', color: '#fca5a5', padding: '10px 14px', borderRadius: 8, fontSize: 13, marginBottom: 14 }}>⚠️ {error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="input-label">Current password</label>
            <input type="password" className="form-input" value={oldPassword} onChange={(e) => setOldPassword(e.target.value)} required />
          </div>
          <div className="input-group">
            <label className="input-label">New password</label>
            <input type="password" className="form-input" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required />
          </div>
          <div className="input-group">
            <label className="input-label">Confirm new password</label>
            <input type="password" className="form-input" value={confirm} onChange={(e) => setConfirm(e.target.value)} required />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 8 }}>
            {!forced && <button type="button" className="btn btn-secondary" onClick={onDone}>Cancel</button>}
            {forced && <button type="button" className="btn btn-secondary" onClick={logout}>Logout</button>}
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Save password'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
