import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function ManagerDashboard() {
  const [team, setTeam] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEmp, setSelectedEmp] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [loadingReport, setLoadingReport] = useState(false);

  useEffect(() => {
    fetchTeam();
  }, []);

  const fetchTeam = () => {
    setLoading(true);
    api.getManagerTeam()
      .then(data => {
        setTeam(data);
        if (data.length > 0) setSelectedEmp(data[0]);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  const handleSelectEmp = async (emp) => {
    setSelectedEmp(emp);
    setLoadingReport(true);
    try {
      const res = await api.getEmployeeReport(emp.userId, emp.role);
      setReportData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingReport(false);
    }
  };

  const downloadReport = () => {
    if (!reportData) return;
    const blob = new Blob([reportData.report_markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedEmp.userId}_readiness_audit_report.md`;
    a.click();
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <div className="spinner" style={{ width: '36px', height: '36px' }}></div>
      </div>
    );
  }

  const readyCount = team.filter(t => t.status === 'READY').length;
  const avgScore = team.length > 0 ? Math.round(team.reduce((acc, t) => acc + (t.readiness_score || 0), 0) / team.length) : 0;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Manager Team Readiness & Oversight</h1>
          <p>Audit and track organizational onboarding health, compliance thresholds, and exportable reports.</p>
        </div>
      </div>

      {/* KPI Overview */}
      <div className="grid-4" style={{ marginBottom: '28px' }}>
        <div className="glass-card">
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>TEAM SIZE</span>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#ffffff', marginTop: '4px' }}>
            {team.length} <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Employees</span>
          </div>
        </div>

        <div className="glass-card">
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>FULLY READY</span>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#34d399', marginTop: '4px' }}>
            {readyCount} <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Verified</span>
          </div>
        </div>

        <div className="glass-card">
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>IN PROGRESS / GAPS</span>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#f59e0b', marginTop: '4px' }}>
            {team.length - readyCount} <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>Employees</span>
          </div>
        </div>

        <div className="glass-card">
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>AVG READINESS</span>
          <div style={{ fontSize: '32px', fontWeight: 800, color: '#818cf8', marginTop: '4px' }}>
            {avgScore}%
          </div>
        </div>
      </div>

      {/* Team Matrix Table */}
      <div className="glass-card" style={{ marginBottom: '28px' }}>
        <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Team Competency Matrix</h3>
        <div className="custom-table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Department</th>
                <th>Role</th>
                <th>Level</th>
                <th>Readiness Score</th>
                <th>Compliance Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {team.map(emp => (
                <tr key={emp.userId} style={{ background: selectedEmp?.userId === emp.userId ? 'rgba(99, 102, 241, 0.08)' : 'transparent' }}>
                  <td>
                    <strong>{emp.name}</strong>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>@{emp.userId}</div>
                  </td>
                  <td>{emp.department}</td>
                  <td>{emp.role}</td>
                  <td>Lvl {emp.level}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ width: '60px', height: '6px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '999px', overflow: 'hidden' }}>
                        <div style={{ width: `${emp.readiness_score}%`, height: '100%', background: emp.readiness_score >= 80 ? '#10b981' : '#f59e0b', borderRadius: '999px' }}></div>
                      </div>
                      <span style={{ fontWeight: 700 }}>{emp.readiness_score}%</span>
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${
                      emp.status === 'READY' ? 'badge-emerald' :
                      emp.status === 'READY WITH GAPS' ? 'badge-amber' : 'badge-rose'
                    }`}>
                      {emp.status}
                    </span>
                  </td>
                  <td>
                    <button
                      className="btn btn-secondary"
                      style={{ padding: '6px 12px', fontSize: '12px' }}
                      onClick={() => handleSelectEmp(emp)}
                    >
                      Audit Details →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Drill Down & Export View */}
      {selectedEmp && (
        <div className="glass-card" style={{ borderLeft: '4px solid var(--primary)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ fontSize: '18px' }}>Individual Audit: {selectedEmp.name}</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                Role: {selectedEmp.role} • Readiness Verdict: <strong>{selectedEmp.status}</strong>
              </p>
            </div>
            <button
              className="btn btn-primary"
              onClick={downloadReport}
              disabled={loadingReport || !reportData}
            >
              📄 Export Readiness Audit Report (.MD)
            </button>
          </div>

          {selectedEmp.missing_topics && selectedEmp.missing_topics.length > 0 && (
            <div style={{ padding: '14px 18px', background: 'rgba(239, 68, 68, 0.08)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(239, 68, 68, 0.25)', marginBottom: '16px' }}>
              <strong style={{ color: '#fca5a5' }}>Identified Bottlenecks & Incomplete Modules:</strong>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' }}>
                {selectedEmp.missing_topics.map((m, i) => (
                  <span key={i} className="badge badge-rose">Needs Completion: {m}</span>
                ))}
              </div>
            </div>
          )}

          {reportData && (
            <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '18px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
              <pre style={{ color: '#cbd5e1', fontSize: '12px', fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                {reportData.report_markdown}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
