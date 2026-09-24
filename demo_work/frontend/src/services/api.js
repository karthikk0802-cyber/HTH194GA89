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

  // Roles & Diagnostic
  getRoles: () => request('/roles'),
  getRoleTopics: (role) => request(`/roles/${encodeURIComponent(role)}/topics`),
  getDiagnosticQuestions: () => request('/diagnostic/questions'),
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
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/admin/docs/upload`, {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error('Upload failed');
    return await res.json();
  }
};
