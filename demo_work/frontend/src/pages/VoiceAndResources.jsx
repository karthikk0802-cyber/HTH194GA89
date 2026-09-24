import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function VoiceAndResources() {
  const [activeTab, setActiveTab] = useState('voice');
  
  // Voice state
  const [mode, setMode] = useState('explain');
  const [transcript, setTranscript] = useState('');
  const [tutorReply, setTutorReply] = useState('');
  const [loadingVoice, setLoadingVoice] = useState(false);

  // Resources state
  const [selectedTopic, setSelectedTopic] = useState('security');
  const [resources, setResources] = useState([]);
  const [loadingResources, setLoadingResources] = useState(false);

  const tutorModes = [
    { id: 'explain', label: 'Explain Concept', icon: '📖' },
    { id: 'quiz-me', label: 'Quiz Me', icon: '❓' },
    { id: 'explain-mistake', label: 'Review Mistake', icon: '🔍' },
    { id: 'give-example', label: 'Give Real Example', icon: '💡' },
    { id: 'what-next', label: 'What Should I Learn Next?', icon: '🧭' }
  ];

  const topicsList = [
    { id: 'company_basics', title: 'Company Basics' },
    { id: 'security', title: 'Security & Compliance' },
    { id: 'git_workflow', title: 'Git Workflow' },
    { id: 'tools', title: 'Tools & Workflows' }
  ];

  useEffect(() => {
    setLoadingResources(true);
    api.getResources(selectedTopic)
      .then(setResources)
      .catch(console.error)
      .finally(() => setLoadingResources(false));
  }, [selectedTopic]);

  const handleVoiceSubmit = async (e) => {
    e.preventDefault();
    if (!transcript.trim()) return;

    setLoadingVoice(true);
    try {
      const res = await api.voiceInteract(transcript, mode);
      setTutorReply(res.reply);
    } catch (err) {
      alert('Voice tutor error: ' + err.message);
    } finally {
      setLoadingVoice(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Voice Tutor & Curated Resources</h1>
          <p>Multi-modal interactive voice coaching with graceful text fallback and verified intranet materials.</p>
        </div>
      </div>

      {/* Tab Selector */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        <button
          className={`btn ${activeTab === 'voice' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '10px 20px', fontSize: '14px' }}
          onClick={() => setActiveTab('voice')}
        >
          🎙️ Interactive Voice Tutor
        </button>
        <button
          className={`btn ${activeTab === 'resources' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ padding: '10px 20px', fontSize: '14px' }}
          onClick={() => setActiveTab('resources')}
        >
          📚 Verified Intranet Resources
        </button>
      </div>

      {/* TAB 1: Voice Tutor */}
      {activeTab === 'voice' && (
        <div className="glass-card" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
            <h3 style={{ fontSize: '18px' }}>Voice Coaching Session</h3>
            <span className="badge badge-indigo">Graceful Fallback Mode Active</span>
          </div>

          {/* Mode Selector */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '24px' }}>
            {tutorModes.map(m => (
              <button
                key={m.id}
                className={`btn ${mode === m.id ? 'btn-primary' : 'btn-secondary'}`}
                style={{ padding: '8px 14px', fontSize: '13px' }}
                onClick={() => setMode(m.id)}
              >
                {m.icon} {m.label}
              </button>
            ))}
          </div>

          {/* Voice Input Simulator */}
          <form onSubmit={handleVoiceSubmit}>
            <div className="input-group">
              <label className="input-label">Simulate Spoken Input (Speech-to-Text Fallback)</label>
              <div style={{ display: 'flex', gap: '10px' }}>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g. 'Can you explain why we don't deploy on Fridays?' or 'Quiz me on API security!'"
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                />
                <button
                  type="submit"
                  className="btn btn-primary"
                  style={{ flexShrink: 0, padding: '0 24px' }}
                  disabled={loadingVoice || !transcript.trim()}
                >
                  {loadingVoice ? <div className="spinner"></div> : '🎙️ Speak to Tutor'}
                </button>
              </div>
            </div>
          </form>

          {/* Tutor Reply Card */}
          {tutorReply && (
            <div style={{
              marginTop: '24px',
              padding: '24px',
              background: 'rgba(99, 102, 241, 0.1)',
              borderRadius: 'var(--radius-lg)',
              border: '1px solid rgba(99, 102, 241, 0.3)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
                <span style={{ fontSize: '24px' }}>🤖</span>
                <strong style={{ color: '#ffffff', fontSize: '16px' }}>AI Voice Tutor Reply:</strong>
              </div>
              <p style={{ fontSize: '15px', color: '#f3f4f6', lineHeight: 1.6 }}>
                {tutorReply}
              </p>
            </div>
          )}
        </div>
      )}

      {/* TAB 2: Curated Resources */}
      {activeTab === 'resources' && (
        <div className="glass-card" style={{ padding: '32px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ fontSize: '18px' }}>Verified Static Intranet Catalog</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                Zero hallucinations: all links originate from an admin-verified internal repository.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              {topicsList.map(t => (
                <button
                  key={t.id}
                  className={`btn ${selectedTopic === t.id ? 'btn-primary' : 'btn-secondary'}`}
                  style={{ padding: '6px 12px', fontSize: '12px' }}
                  onClick={() => setSelectedTopic(t.id)}
                >
                  {t.title}
                </button>
              ))}
            </div>
          </div>

          {loadingResources ? (
            <div style={{ textAlign: 'center', padding: '40px' }}><div className="spinner"></div></div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
              {resources.map((r, i) => (
                <div
                  key={i}
                  style={{
                    padding: '20px',
                    background: 'rgba(15, 23, 42, 0.6)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-md)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between'
                  }}
                >
                  <div>
                    <span className={`badge ${
                      r.type === 'Video' ? 'badge-rose' :
                      r.type === 'Document' ? 'badge-indigo' :
                      r.type === 'SOP' ? 'badge-cyan' : 'badge-emerald'
                    }`} style={{ marginBottom: '10px' }}>
                      {r.type}
                    </span>
                    <h4 style={{ fontSize: '16px', color: '#ffffff', marginBottom: '8px' }}>{r.title}</h4>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{r.url}</span>
                  </div>
                  <a
                    href={r.url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn btn-secondary"
                    style={{ marginTop: '16px', padding: '8px', fontSize: '12px', textAlign: 'center' }}
                  >
                    Open Verified Document ↗
                  </a>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
