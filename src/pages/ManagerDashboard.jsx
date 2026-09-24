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
    return <span className="spinner spinner-lg" />;
  }

  const readyCount = team.filter(t => t.status === 'READY').length;
  const avgScore = team.length > 0 ? Math.round(team.reduce((acc, t) => acc + (t.readiness_score || 0), 0) / team.length) : 0;

  return (
    <div>
      <div className="page-header">
        <h1><span className="kicker">01</span>Team readiness</h1>
        <p>Onboarding health across the org, with exportable audits.</p>
      </div>

      <div className="section">
        <div className="row" style={{ gap: 48 }}>
          <div>
            <div className="kpi-label">Team</div>
            <div className="kpi">{team.length}</div>
          </div>
          <div>
            <div className="kpi-label">Ready</div>
            <div className="kpi">{readyCount}</div>
          </div>
          <div>
            <div className="kpi-label">With gaps</div>
            <div className="kpi">{team.length - readyCount}</div>
          </div>
          <div>
            <div className="kpi-label">Avg readiness</div>
            <div className="kpi">{avgScore}%</div>
          </div>
        </div>
      </div>

      <div className="section">
        <div className="sec-head">
          <h3><span className="idx">02</span>Roster</h3>
        </div>
        <div className="custom-table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>Employee</th>
                <th>Department</th>
                <th>Role</th>
                <th>Level</th>
                <th>Readiness</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {team.map(emp => (
                <tr key={emp.userId}>
                  <td>
                    <strong>{emp.name}</strong>
                    <div className="cell-sub">@{emp.userId}</div>
                  </td>
                  <td>{emp.department}</td>
                  <td>{emp.role}</td>
                  <td>Lvl {emp.level}</td>
                  <td><strong>{emp.readiness_score}%</strong></td>
                  <td>
                    <span className={`badge ${
                      emp.status === 'READY' ? 'badge-emerald' :
                      emp.status === 'READY WITH GAPS' ? 'badge-amber' : 'badge-rose'
                    }`}>
                      {emp.status}
                    </span>
                  </td>
                  <td>
                    <button className="btn btn-sm btn-secondary" onClick={() => handleSelectEmp(emp)}>
                      Audit →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedEmp && (
        <div className="section">
          <div className="sec-head">
            <h3><span className="idx">03</span>{selectedEmp.name}</h3>
            <button className="btn btn-sm btn-primary" onClick={downloadReport} disabled={loadingReport || !reportData}>
              Export report (.md)
            </button>
          </div>
          <p className="sub">{selectedEmp.role} · Verdict: {selectedEmp.status}</p>

          {selectedEmp.missing_topics && selectedEmp.missing_topics.length > 0 && (
            <div className="mt">
              <span className="kpi-label">Incomplete modules</span>
              <div className="row mt">
                {selectedEmp.missing_topics.map((m, i) => (
                  <span key={i} className="badge badge-rose">{m}</span>
                ))}
              </div>
            </div>
          )}

          {reportData && (
            <pre className="mono mt" style={{ fontSize: 12, whiteSpace: 'pre-wrap', borderTop: '1px solid var(--line)', paddingTop: 16 }}>
              {reportData.report_markdown}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
