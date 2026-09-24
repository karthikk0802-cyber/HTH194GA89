import React, { useState, useEffect } from 'react';
import './App.css';
import { AuthProvider, useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';

// Pages
import Login from './pages/Login';
import AdminLogin from './pages/AdminLogin';
import UserManagement from './pages/UserManagement';
import Dashboard from './pages/Dashboard';
import PreAssessment from './pages/PreAssessment';
import PreAssessmentV2 from './pages/PreAssessmentV2';
import LearningPath from './pages/LearningPath';
import QandA from './pages/QandA';
import QuizPractice from './pages/QuizPractice';
import QuizPracticeV2 from './pages/QuizPracticeV2';
import AppliedScenarios from './pages/AppliedScenarios';
import VoiceAndResources from './pages/VoiceAndResources';
import ManagerDashboard from './pages/ManagerDashboard';
import AdminCenter from './pages/AdminCenter';
import ChangePassword from './components/ChangePassword';

const QUIZ_V2 = import.meta.env.VITE_QUIZ_V2 === 'true';

function MainApp() {
  const { isAuthenticated, user, token } = useAuth();
  const isAdmin = !!user?.is_admin && (token || '').startsWith('admin_token_');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedRole, setSelectedRole] = useState(user?.role || 'Software Engineer');
  const [selectedQuizTopic, setSelectedQuizTopic] = useState('');
  const [adminView, setAdminView] = useState(false);

  // Role is admin-assigned: view always follows the logged-in user's record.
  useEffect(() => {
    if (user?.role) setSelectedRole(user.role);
  }, [user?.role]);

  // Admins get the admin portal only — no learner content.
  const ADMIN_TABS = ['admin-users', 'admin'];
  useEffect(() => {
    if (isAdmin && !ADMIN_TABS.includes(activeTab)) setActiveTab('admin-users');
  }, [isAdmin]);

  if (!isAuthenticated) {
    if (adminView) return <AdminLogin onBack={() => setAdminView(false)} />;
    return <Login onAdmin={() => setAdminView(true)} />;
  }

  const renderContent = () => {
    if (isAdmin) {
      if (activeTab === 'admin') return <AdminCenter />;
      return <UserManagement />;
    }
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard selectedRole={selectedRole} setActiveTab={setActiveTab} />;
      case 'pre-assessment':
        if (QUIZ_V2) {
          return (
            <PreAssessmentV2
              selectedRole={selectedRole}
              setActiveTab={setActiveTab}
            />
          );
        }
        return (
          <PreAssessment
            selectedRole={selectedRole}
            setActiveTab={setActiveTab}
          />
        );
      case 'learning-path':
        return (
          <LearningPath
            selectedRole={selectedRole}
            setActiveTab={setActiveTab}
            setSelectedQuizTopic={setSelectedQuizTopic}
          />
        );
      case 'qa':
        return <QandA selectedRole={selectedRole} />;
      case 'quiz':
        if (QUIZ_V2) {
          return (
            <QuizPracticeV2
              selectedRole={selectedRole}
              selectedQuizTopic={selectedQuizTopic}
            />
          );
        }
        return (
          <QuizPractice
            selectedRole={selectedRole}
            selectedQuizTopic={selectedQuizTopic}
          />
        );
      case 'scenarios':
        return <AppliedScenarios />;
      case 'voice-resources':
        return <VoiceAndResources />;
      case 'manager':
        return <ManagerDashboard />;
      case 'admin':
        return <AdminCenter />;
      default:
        return <Dashboard selectedRole={selectedRole} setActiveTab={setActiveTab} />;
    }
  };

  return (
    <div className="app-layout">
      {user?.must_change_password && <ChangePassword forced />}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} isAdmin={isAdmin} />
      <div className="main-content-wrapper">
        <Navbar
          activeTab={activeTab}
          selectedRole={selectedRole}
        />
        <main className="content-container">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
