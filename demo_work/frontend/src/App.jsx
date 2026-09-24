import React, { useState } from 'react';
import './App.css';
import { AuthProvider, useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';

// Pages
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import PreAssessment from './pages/PreAssessment';
import LearningPath from './pages/LearningPath';
import QandA from './pages/QandA';
import QuizPractice from './pages/QuizPractice';
import AppliedScenarios from './pages/AppliedScenarios';
import VoiceAndResources from './pages/VoiceAndResources';
import ManagerDashboard from './pages/ManagerDashboard';
import AdminCenter from './pages/AdminCenter';

function MainApp() {
  const { isAuthenticated, user } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedRole, setSelectedRole] = useState(user?.role || 'Software Engineer');
  const [selectedQuizTopic, setSelectedQuizTopic] = useState('');

  if (!isAuthenticated) {
    return <Login />;
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard selectedRole={selectedRole} setActiveTab={setActiveTab} />;
      case 'pre-assessment':
        return (
          <PreAssessment
            selectedRole={selectedRole}
            setSelectedRole={setSelectedRole}
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
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="main-content-wrapper">
        <Navbar
          activeTab={activeTab}
          selectedRole={selectedRole}
          setSelectedRole={setSelectedRole}
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
