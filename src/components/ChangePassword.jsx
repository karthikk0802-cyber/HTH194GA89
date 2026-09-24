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
    <div className={forced ? 'modal-veil' : ''}>
      <div className={forced ? 'modal' : 'card'}>
        <div className="modal-h">
          <h3>{forced ? 'Set your password to continue' : 'Change password'}</h3>
          {!forced && <button className="modal-x" onClick={onDone}>✕</button>}
        </div>
        <p style={{ fontSize: 13, color: 'var(--muted)', marginBottom: 16 }}>
          {forced
            ? 'Your account still uses the default first-login password. Choose a personal password.'
            : 'Enter your current password, then choose a new one (min 8 characters).'}
        </p>
        {error && <div className="notice notice-error">{error}</div>}
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
          <div className="row-end">
            {!forced && <button type="button" className="btn btn-secondary" onClick={onDone}>Cancel</button>}
            {forced && <button type="button" className="btn btn-secondary" onClick={logout}>Sign out</button>}
            <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Save password'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}
