import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function VoiceAndResources() {
  const [activeTab, setActiveTab] = useState('voice');

  const [mode, setMode] = useState('explain');
  const [transcript, setTranscript] = useState('');
  const [tutorReply, setTutorReply] = useState('');
  const [loadingVoice, setLoadingVoice] = useState(false);

  const [selectedTopic, setSelectedTopic] = useState('security');
  const [resources, setResources] = useState([]);
  const [loadingResources, setLoadingResources] = useState(false);

  const tutorModes = [
    { id: 'explain', label: 'Explain' },
    { id: 'quiz-me', label: 'Quiz me' },
    { id: 'explain-mistake', label: 'Review mistake' },
    { id: 'give-example', label: 'Give example' },
    { id: 'what-next', label: 'What next' }
  ];

  const topicsList = [
    { id: 'company_basics', title: 'Company Basics' },
    { id: 'security', title: 'Security' },
    { id: 'git_workflow', title: 'Git Workflow' },
    { id: 'tools', title: 'Tools' }
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
        <h1><span className="kicker">01</span>Voice & Resources</h1>
        <p>Spoken-style coaching with text fallback, plus the verified intranet catalog.</p>
      </div>

      <div className="row" style={{ marginBottom: 32 }}>
        <button className={`btn btn-sm ${activeTab === 'voice' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('voice')}>
          Voice tutor
        </button>
        <button className={`btn btn-sm ${activeTab === 'resources' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setActiveTab('resources')}>
          Intranet resources
        </button>
      </div>

      {activeTab === 'voice' && (
        <div className="section">
          <div className="sec-head">
            <h3><span className="idx">02</span>Ask out loud, in text</h3>
            <span className="note">text fallback active</span>
          </div>
          <div className="row" style={{ marginBottom: 16 }}>
            {tutorModes.map(m => (
              <button
                key={m.id}
                className={`btn btn-sm ${mode === m.id ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setMode(m.id)}
              >
                {m.label}
              </button>
            ))}
          </div>

          <form onSubmit={handleVoiceSubmit}>
            <div className="row">
              <input
                type="text"
                className="form-input"
                style={{ flex: 1, minWidth: 240 }}
                placeholder="Type what you'd say — e.g. why no Friday deploys?"
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
              />
              <button type="submit" className="btn btn-primary" disabled={loadingVoice || !transcript.trim()}>
                {loadingVoice ? <span className="spinner" /> : 'Ask tutor'}
              </button>
            </div>
          </form>

          {tutorReply && (
            <div className="callout callout-info mt">
              <h4>Tutor reply</h4>
              <p>{tutorReply}</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'resources' && (
        <div className="section">
          <div className="sec-head">
            <h3><span className="idx">02</span>Verified catalog</h3>
            <span className="row">
              {topicsList.map(t => (
                <button
                  key={t.id}
                  className={`btn btn-sm ${selectedTopic === t.id ? 'btn-primary' : 'btn-secondary'}`}
                  onClick={() => setSelectedTopic(t.id)}
                >
                  {t.title}
                </button>
              ))}
            </span>
          </div>

          {loadingResources ? (
            <span className="spinner spinner-lg" />
          ) : (
            <div>
              {resources.map((r, i) => (
                <div key={i} className="dir-row">
                  <div>
                    <div>
                      <div className="dir-main">{r.title}</div>
                      <div className="dir-sub">{r.type} · {r.url}</div>
                    </div>
                    <a href={r.url} target="_blank" rel="noreferrer" className="btn btn-sm btn-secondary">Open →</a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
