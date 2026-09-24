import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('onboardiq_user');
    return saved ? JSON.parse(saved) : {
      id: 1,
      username: 'sarah_engineer',
      email: 'sarah@nexora.com',
      full_name: 'Sarah Jenkins',
      role: 'Software Engineer',
      department: 'Core Platform',
      is_admin: false
    };
  });
  
  const [token, setToken] = useState(() => localStorage.getItem('onboardiq_token') || 'demo_token');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (user) {
      localStorage.setItem('onboardiq_user', JSON.stringify(user));
    } else {
      localStorage.removeItem('onboardiq_user');
    }
  }, [user]);

  useEffect(() => {
    if (token) {
      localStorage.setItem('onboardiq_token', token);
    } else {
      localStorage.removeItem('onboardiq_token');
    }
  }, [token]);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const res = await api.login(username, password);
      setUser(res.user);
      setToken(res.token);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || 'Login failed' };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    try {
      const res = await api.register(userData);
      setUser(res.user);
      setToken(res.token);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || 'Registration failed' };
    } finally {
      setLoading(false);
    }
  };

  const quickSwitchUser = (selectedUser) => {
    setUser(selectedUser);
    setToken(`token_${selectedUser.username}_${selectedUser.id}`);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('onboardiq_user');
    localStorage.removeItem('onboardiq_token');
  };

  const updateRole = (newRole) => {
    if (user) {
      setUser(prev => ({ ...prev, role: newRole }));
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      login,
      register,
      quickSwitchUser,
      logout,
      updateRole,
      isAuthenticated: !!user
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
