import React, { useState, useEffect, useMemo } from 'react';
import { api } from '../services/api';

const EMPTY = { username: '', email: '', password: 'employee@123', full_name: '', role: 'Backend Engineer', department: 'Engineering - Core Platform', buddy: '' };
const RESUME_ENABLED = import.meta.env.VITE_RESUME_PROFILE === 'true';

export default function UserManagement() {
  const token = localStorage.getItem('onboardiq_token') || '';
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState(EMPTY);
  const [editing, setEditing] = useState(null);
  const [editVals, setEditVals] = useState({ role: '', department: '', buddy: '' });
  const [saving, setSaving] = useState(false);
  const [taxonomy, setTaxonomy] = useState({ departments: {}, role_cards: {} });
  const [profiles, setProfiles] = useState({});
  const [uploadingFor, setUploadingFor] = useState(null);

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const [uData, tax] = await Promise.all([
        api.adminListUsers(token),
        api.getTaxonomy().catch(() => null),
      ]);
      setUsers(uData);
      if (tax) setTaxonomy(tax);
    } catch (err) {
      setError(err.message || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const departments = useMemo(() => Object.keys(taxonomy.departments || {}), [taxonomy]);
  const allRoles = useMemo(() => Object.keys(taxonomy.role_cards || {}), [taxonomy]);
  const rolesForDept = (dept) => {
    const list = (taxonomy.departments || {})[dept];
    return Array.isArray(list) && list.length > 0 ? list : allRoles;
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.adminCreateUser(token, form);
      setForm(EMPTY);
      await load();
    } catch (err) {
      alert('Create failed: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const startEdit = (u) => {
    setEditing(u.username);
    setEditVals({ role: u.role, department: u.department, buddy: u.buddy || '' });
  };

  const handleUpdate = async (username) => {
    try {
      await api.adminUpdateUser(token, username, { role: editVals.role, department: editVals.department, buddy: editVals.buddy });
      setEditing(null);
      await load();
    } catch (err) {
      alert('Update failed: ' + err.message);
    }
  };

  const handleDelete = async (username) => {
    if (!window.confirm(`Delete user ${username}? Removes profile + topic states.`)) return;
    try {
      await api.adminDeleteUser(token, username);
      await load();
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  const handleReset = async (username) => {
    if (!window.confirm(`Reset learning baseline for ${username}?`)) return;
    try {
      await api.adminResetBaseline(token, username);
      alert('Baseline reset for ' + username);
    } catch (err) {
      alert('Reset failed: ' + err.message);
    }
  };

  const handleTransfer = async (username) => {
    if (!window.confirm(`Transfer ${username} to ${editVals.role} / ${editVals.department}? Shared-topic mastery is kept, the rest is dropped.`)) return;
    try {
      const res = await api.adminTransferRole(token, username, editVals.role, editVals.department);
      setEditing(null);
      await load();
      alert(`Transferred. Kept: ${res.kept_topics.join(', ') || 'none'}. Dropped: ${res.dropped_topics.join(', ') || 'none'}.`);
    } catch (err) {
      alert('Transfer failed: ' + err.message);
    }
  };

  const handleResumeUpload = async (username, role, file) => {
    if (!file) return;
    setUploadingFor(username);
    try {
      const res = await api.uploadResume(token, username, role, file);
      setProfiles((p) => ({ ...p, [username]: res.profile }));
    } catch (err) {
      alert('Resume upload failed: ' + err.message);
    } finally {
      setUploadingFor(null);
    }
  };

  const handleResumeDelete = async (username) => {
    if (!window.confirm(`Delete stored resume profile for ${username}?`)) return;
    try {
      await api.deleteResumeProfile(token, username);
      setProfiles((p) => {
        const next = { ...p };
        delete next[username];
        return next;
      });
    } catch (err) {
      alert('Delete failed: ' + err.message);
    }
  };

  if (loading) return <span className="spinner spinner-lg" />;

  return (
    <div>
      <div className="page-header">
        <h1><span className="kicker">01</span>Users</h1>
        <p>Admin-only. Create, edit, reset, delete. First-login password is <code>employee@123</code>; users must change it on sign-in.</p>
      </div>
      {error && <div className="notice notice-error">{error} — sign in via the admin portal.</div>}

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">02</span>New user</h3>
        </div>
        <form onSubmit={handleCreate}>
          <div className="grid-3">
            <div className="input-group">
              <label className="input-label">Username</label>
              <input className="form-input" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
            </div>
            <div className="input-group">
              <label className="input-label">Email</label>
              <input className="form-input" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            </div>
            <div className="input-group">
              <label className="input-label">Full name</label>
              <input className="form-input" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
            </div>
            <div className="input-group">
              <label className="input-label">Password</label>
              <input className="form-input" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            </div>
            <div className="input-group">
              <label className="input-label">Department</label>
              <select className="form-select" value={form.department} onChange={(e) => {
                const department = e.target.value;
                const valid = rolesForDept(department);
                setForm((f) => ({ ...f, department, role: valid.includes(f.role) ? f.role : (valid[0] || '') }));
              }}>
                {departments.map((d) => <option key={d} value={d}>{d}</option>)}
              </select>
            </div>
            <div className="input-group">
              <label className="input-label">Role</label>
              <select className="form-select" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
                {rolesForDept(form.department).map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div className="input-group">
              <label className="input-label">Buddy (username, optional)</label>
              <input className="form-input" placeholder="sarah_engineer" value={form.buddy} onChange={(e) => setForm({ ...form, buddy: e.target.value })} />
            </div>
          </div>
          <button className="btn btn-primary" disabled={saving}>{saving ? 'Creating…' : 'Create user'}</button>
        </form>
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">03</span>Roster</h3>
          <span className="note">{users.length} accounts</span>
        </div>
        <div className="custom-table-container">
          <table className="custom-table">
            <thead><tr><th>User</th><th>Role</th><th>Department</th><th>Buddy</th><th>Admin</th><th></th></tr></thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.username}>
                  <td>
                    <strong>{u.username}</strong>
                    <div className="cell-sub">{u.full_name} · {u.email}</div>
                    {u.buddy && <div className="cell-sub">Buddy: {u.buddy}</div>}
                    {RESUME_ENABLED && profiles[u.username] && (
                      <div className="cell-sub">Resume: {profiles[u.username].seniority} · {Object.keys(profiles[u.username].topic_adjustments || {}).length} calibrated topics</div>
                    )}
                  </td>
                  <td>{editing === u.username
                    ? <select className="form-select" value={editVals.role} onChange={(e) => setEditVals((v) => ({ ...v, role: e.target.value }))}>
                        {rolesForDept(editVals.department).map((r) => <option key={r} value={r}>{r}</option>)}
                      </select>
                    : u.role}</td>
                  <td>{editing === u.username
                    ? <select className="form-select" value={editVals.department} onChange={(e) => {
                        const department = e.target.value;
                        const valid = rolesForDept(department);
                        setEditVals((v) => ({ department, role: valid.includes(v.role) ? v.role : (valid[0] || '') }));
                      }}>
                        {departments.map((d) => <option key={d} value={d}>{d}</option>)}
                      </select>
                    : u.department}</td>
                  <td>{editing === u.username
                    ? <input className="form-input" value={editVals.buddy} placeholder="buddy username" onChange={(e) => setEditVals((v) => ({ ...v, buddy: e.target.value }))} />
                    : (u.buddy || '—')}</td>
                  <td>{u.is_admin ? 'yes' : '—'}</td>
                  <td>
                    <div className="row">
                      {editing === u.username ? (
                        <>
                          <button className="btn btn-sm btn-primary" onClick={() => handleUpdate(u.username)}>Save</button>
                          <button className="btn btn-sm btn-secondary" onClick={() => handleTransfer(u.username)}>Transfer role</button>
                          <button className="btn btn-sm btn-secondary" onClick={() => setEditing(null)}>Cancel</button>
                        </>
                      ) : (
                        <button className="btn btn-sm btn-secondary" onClick={() => startEdit(u)}>Edit</button>
                      )}
                      <button className="btn btn-sm btn-secondary" onClick={() => handleReset(u.username)}>Reset</button>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(u.username)}>Delete</button>
                    </div>
                    {RESUME_ENABLED && (
                      <div className="row mt">
                        {profiles[u.username] ? (
                          <button className="btn btn-sm btn-secondary" onClick={() => handleResumeDelete(u.username)}>Remove resume profile</button>
                        ) : (
                          <label className="btn btn-sm btn-secondary" style={{ cursor: 'pointer' }}>
                            {uploadingFor === u.username ? 'Parsing…' : 'Upload resume'}
                            <input type="file" accept=".pdf,.docx,.txt" hidden disabled={uploadingFor === u.username}
                              onChange={(e) => handleResumeUpload(u.username, u.role, e.target.files[0])} />
                          </label>
                        )}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
