import React, { useState, useEffect, useMemo } from 'react';
import { api } from '../services/api';

const DEFAULT_FIRST_PASSWORD = 'employee@123';
const EMPTY = { username: '', email: '', password: DEFAULT_FIRST_PASSWORD, full_name: '', role: 'Backend Engineer', department: 'Engineering - Core Platform' };
const RESUME_ENABLED = import.meta.env.VITE_RESUME_PROFILE === 'true';

export default function UserManagement() {
  const token = localStorage.getItem('onboardiq_token') || '';
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState(EMPTY);
  const [editing, setEditing] = useState(null); // username being edited
  const [editVals, setEditVals] = useState({ role: '', department: '' });
  const [saving, setSaving] = useState(false);
  const [taxonomy, setTaxonomy] = useState({ departments: {}, role_cards: {} });
  const [profiles, setProfiles] = useState({}); // username -> resume profile record
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
    setEditVals({ role: u.role, department: u.department });
  };

  const handleUpdate = async (username) => {
    try {
      await api.adminUpdateUser(token, username, { role: editVals.role, department: editVals.department });
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
    if (!window.confirm(`Delete stored resume profile for ${username}? Raw resume was never kept; this removes the extracted skills.`)) return;
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

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}><div className="spinner" /></div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>User Management</h1>
          <p>Admin-only: create, edit, reset baseline, and delete users. No public self-registration.</p>
        </div>
      </div>
      {error && <div className="glass-card" style={{ border: '1px solid var(--accent-rose)', marginBottom: 16 }}>⚠️ {error} — ensure you signed in via the admin portal (admin_token_...).</div>}

      <div className="glass-card" style={{ marginBottom: 24, padding: 24 }}>
        <h3 style={{ marginBottom: 12 }}>Create user</h3>
        <form onSubmit={handleCreate} style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
          <input className="form-input" placeholder="username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
          <input className="form-input" placeholder="email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <input className="form-input" placeholder="full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
          <input className="form-input" placeholder="password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
          <div style={{ gridColumn: '1 / -1', fontSize: 12, color: 'var(--text-muted)' }}>
            Default first-login password is <code>employee@123</code> (server default, overridable via <code>DEFAULT_EMPLOYEE_PASSWORD</code>). User is forced to change it on first sign-in.
          </div>
          <select className="form-select" value={form.department} onChange={(e) => {
            const department = e.target.value;
            const valid = rolesForDept(department);
            setForm((f) => ({ ...f, department, role: valid.includes(f.role) ? f.role : (valid[0] || '') }));
          }}>
            {departments.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
          <select className="form-select" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
            {rolesForDept(form.department).map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
          <div><button className="btn btn-primary" disabled={saving}>{saving ? 'Creating…' : 'Create user'}</button></div>
        </form>
      </div>

      <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="custom-table">
          <thead><tr><th>Username</th><th>Name / Email</th><th>Role</th><th>Department</th><th>Admin</th><th>Actions</th></tr></thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.username}>
                <td><strong>{u.username}</strong></td>
                <td><div>{u.full_name}</div><div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{u.email}</div></td>
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
                <td>{u.is_admin ? 'yes' : 'no'}</td>
                <td>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {editing === u.username ? (
                      <>
                        <button className="btn btn-primary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={() => handleUpdate(u.username)}>Save</button>
                        <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={() => setEditing(null)}>Cancel</button>
                      </>
                    ) : (
                      <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={() => startEdit(u)}>Edit</button>
                    )}
                    <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11 }} onClick={() => handleReset(u.username)}>Reset baseline</button>
                    <button className="btn btn-danger" style={{ padding: '4px 10px', fontSize: 11 }} onClick={() => handleDelete(u.username)}>Delete</button>
                  </div>
                  {RESUME_ENABLED && (
                    <div style={{ marginTop: 8, fontSize: 11 }}>
                      {profiles[u.username] ? (
                        <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
                          <span className="badge badge-emerald">
                            📄 {profiles[u.username].seniority} · {Object.keys(profiles[u.username].topic_adjustments || {}).length} calibrated topics
                          </span>
                          <button className="btn btn-secondary" style={{ padding: '2px 8px', fontSize: 10 }} onClick={() => handleResumeDelete(u.username)}>Remove profile</button>
                        </div>
                      ) : (
                        <label className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: 11, cursor: 'pointer' }}>
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
  );
}
