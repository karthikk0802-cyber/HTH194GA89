const API_BASE = 'http://localhost:8000/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  try {
    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'API request failed');
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error on ${endpoint}:`, error);
    throw error;
  }
}

export const api = {
  // Auth (auth.db)
  login: (username, password) =>
    request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  
  register: (data) =>
    request('/auth/register', { method: 'POST', body: JSON.stringify(data) }),

  getUsers: () => request('/auth/users'),
  
  getMe: (userId) => request(`/auth/me?userId=${encodeURIComponent(userId)}`),

  changePassword: (username, oldPassword, newPassword) =>
    request('/auth/change-password', { method: 'POST', body: JSON.stringify({ username, old_password: oldPassword, new_password: newPassword }) }),

  // Roles & Diagnostic
  getRoles: () => request('/roles'),
  getRoleTopics: (role) => request(`/roles/${encodeURIComponent(role)}/topics`),
  getDiagnosticQuestions: (role = 'Software Engineer', count = 10) =>
    request(`/diagnostic/questions?role=${encodeURIComponent(role)}&count=${encodeURIComponent(count)}`),
  submitDiagnostic: (userId, role, answers) =>
    request('/diagnostic/evaluate', {
      method: 'POST',
      body: JSON.stringify({ userId, role, answers })
    }),


  // Learning Path & Adaptive
  getLearningPath: (userId, role) =>
    request(`/learning-path/${encodeURIComponent(userId)}?role=${encodeURIComponent(role || 'Software Engineer')}`),

  // RAG Q&A
  askQA: (query, role) =>
    request('/qa/ask', { method: 'POST', body: JSON.stringify({ query, role }) }),

  // Quizzes & Remediation
  generateQuiz: (topic, role = 'all', difficulty = 'Beginner') =>
    request(`/quiz/generate?topic=${encodeURIComponent(topic)}&role=${encodeURIComponent(role)}&difficulty=${encodeURIComponent(difficulty)}`),

  startQuizSession: (topic, role = 'all', difficulty = 'Beginner', count = 20) =>
    request(`/quiz/session?topic=${encodeURIComponent(topic)}&role=${encodeURIComponent(role)}&difficulty=${encodeURIComponent(difficulty)}&count=${encodeURIComponent(count)}`),
  
  submitQuiz: (userId, topicId, selectedAnswer, correctAnswer) =>
    request('/quiz/submit', {
      method: 'POST',
      body: JSON.stringify({ userId, topicId, selectedAnswer, correctAnswer })
    }),

  getRemediation: (question, userAnswer, correctAnswer, evidenceQuote) =>
    request('/quiz/remediation', {
      method: 'POST',
      body: JSON.stringify({ question, userAnswer, correctAnswer, evidenceQuote })
    }),

  getExplainAgain: (question, userAnswer, correctAnswer, previousExplanation) =>
    request('/quiz/explain-again', {
      method: 'POST',
      body: JSON.stringify({ question, userAnswer, correctAnswer, previousExplanation })
    }),

  submitQuizFeedback: (questionText, reason, comments) =>
    request('/quiz/feedback', {
      method: 'POST',
      body: JSON.stringify({ questionText, reason, comments })
    }),

  // Scenarios & Voice
  getScenarios: () => request('/scenarios'),
  evaluateScenario: (userId, scenarioId, userResponse) =>
    request('/scenarios/evaluate', {
      method: 'POST',
      body: JSON.stringify({ userId, scenarioId, userResponse })
    }),

  voiceInteract: (transcript, mode) =>
    request('/voice/interact', {
      method: 'POST',
      body: JSON.stringify({ transcript, mode })
    }),

  getResources: (topicId) => request(`/resources/${encodeURIComponent(topicId)}`),

  // Employee Dashboard
  getDashboardSummary: (userId, role) =>
    request(`/dashboard/${encodeURIComponent(userId)}?role=${encodeURIComponent(role || 'Software Engineer')}`),

  // Manager Oversight
  getManagerTeam: () => request('/manager/team'),
  getEmployeeReport: (userId, role) =>
    request(`/manager/report/${encodeURIComponent(userId)}?role=${encodeURIComponent(role || 'Software Engineer')}`),

  // Admin Knowledge Base
  getDocuments: () => request('/admin/docs'),
  toggleDocument: (docId) => request(`/admin/docs/toggle/${docId}`, { method: 'POST' }),
  deleteDocument: (docId) => request(`/admin/docs/${docId}`, { method: 'DELETE' }),
  getFeedbackList: () => request('/admin/feedback'),
  approveDocument: (docId) => request(`/admin/docs/approve/${docId}`, { method: 'POST' }),
  uploadDocument: async (file, owner = '') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('owner', owner);
    const res = await fetch(`${API_BASE}/admin/docs/upload`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Upload failed');
    return await res.json();
  },

  // Admin portal (separate admin token; existing auth functions untouched)
  adminLogin: (username, password) =>
    request('/admin/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  adminListUsers: (token) =>
    request('/admin/users', { headers: { Authorization: `Bearer ${token}` } }),
  adminCreateUser: (token, data) =>
    request('/admin/users', { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: JSON.stringify(data) }),
  adminUpdateUser: (token, username, data) =>
    request(`/admin/users/${encodeURIComponent(username)}`, { method: 'PUT', headers: { Authorization: `Bearer ${token}` }, body: JSON.stringify(data) }),
  adminDeleteUser: (token, username) =>
    request(`/admin/users/${encodeURIComponent(username)}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } }),
  adminResetBaseline: (token, username) =>
    request(`/admin/users/${encodeURIComponent(username)}/reset-baseline`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } }),

  // Adaptive quiz v2 (wrappers; v1 functions untouched)
  getTaxonomy: () => request('/taxonomy'),
  getBaselineQuestions: (role, perTopic = 3, userId = '') =>
    request(`/v2/diagnostic/questions?role=${encodeURIComponent(role)}&per_topic=${encodeURIComponent(perTopic)}${userId ? `&userId=${encodeURIComponent(userId)}` : ''}`),
  submitBaseline: (userId, role, answers) =>
    request('/v2/diagnostic/evaluate', { method: 'POST', body: JSON.stringify({ userId, role, answers }) }),
  getQuizNext: (userId, role) =>
    request(`/v2/quiz/next?userId=${encodeURIComponent(userId)}&role=${encodeURIComponent(role || 'Software Engineer')}`),
  generatePersonalizedQuiz: (topic, role = 'all', userId = '') =>
    request(`/v2/quiz/generate?topic=${encodeURIComponent(topic)}&role=${encodeURIComponent(role)}&userId=${encodeURIComponent(userId)}`),
  startPersonalizedSession: (topic, role = 'all', userId = '', count = 20) =>
    request(`/v2/quiz/session?topic=${encodeURIComponent(topic)}&role=${encodeURIComponent(role)}&userId=${encodeURIComponent(userId)}&count=${encodeURIComponent(count)}`),

  // Held-out graded eval (measures, never pays XP) + buddy + transfer
  getGradedEval: (userId, role) =>
    request(`/v2/eval?userId=${encodeURIComponent(userId)}&role=${encodeURIComponent(role || 'Software Engineer')}`),
  submitGradedEval: (userId, role, answers) =>
    request('/v2/eval/submit', { method: 'POST', body: JSON.stringify({ userId, role, answers }) }),
  getBuddyAttention: (username) =>
    request(`/buddy/${encodeURIComponent(username)}/attention`),
  managerSignoff: (userId, signer, topicId = null, note = '') =>
    request('/manager/signoff', { method: 'POST', body: JSON.stringify({ userId, signer, topicId, note }) }),
  adminTransferRole: (token, username, newRole, newDepartment) =>
    request(`/admin/users/${encodeURIComponent(username)}/transfer`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: JSON.stringify({ new_role: newRole, new_department: newDepartment }) }),

  // Resume profiles (admin-only)
  uploadResume: async (token, userId, role, file) => {
    const formData = new FormData();
    formData.append('userId', userId);
    formData.append('role', role);
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/v2/profile/resume`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Resume upload failed');
    }
    return await res.json();
  },
  getResumeProfile: (token, userId) =>
    request(`/v2/profile/${encodeURIComponent(userId)}`, { headers: { Authorization: `Bearer ${token}` } }),
  deleteResumeProfile: (token, userId) =>
    request(`/v2/profile/${encodeURIComponent(userId)}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } }),
};
