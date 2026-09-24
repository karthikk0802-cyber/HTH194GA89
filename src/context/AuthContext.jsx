import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
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
  const [profileStats, setProfileStats] = useState({ xp: 0, level: 1, streak_days: 1 });
  const [loading, setLoading] = useState(false);

  const fetchProfileStats = useCallback(async (username, role) => {
    if (!username) return;
    try {
      const data = await api.getDashboardSummary(username, role || 'Software Engineer');
      if (data) {
        setProfileStats({
          xp: data.xp || 0,
          level: data.level || 1,
          streak_days: data.streak_days || 1,
          readiness_percentage: data.readiness_percentage || 0
        });
      }
    } catch (err) {
      console.warn('Could not fetch user profile stats:', err);
    }
  }, []);

  useEffect(() => {
    if (user) {
      localStorage.setItem('onboardiq_user', JSON.stringify(user));
      fetchProfileStats(user.username, user.role);
    } else {
      localStorage.removeItem('onboardiq_user');
    }
  }, [user, fetchProfileStats]);

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
      await fetchProfileStats(res.user.username, res.user.role);
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
      await fetchProfileStats(res.user.username, res.user.role);
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
    fetchProfileStats(selectedUser.username, selectedUser.role);
  };

  const changePassword = async (username, oldPassword, newPassword) => {
    try {
      const res = await api.changePassword(username, oldPassword, newPassword);
      setUser(res.user);
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message || 'Password change failed' };
    }
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
      fetchProfileStats(user.username, newRole);
    }
  };

  const updateXpPoints = (newXp, newLevel) => {
    setProfileStats(prev => ({
      ...prev,
      xp: newXp !== undefined ? newXp : prev.xp,
      level: newLevel !== undefined ? newLevel : (newXp !== undefined ? Math.floor(newXp / 100) + 1 : prev.level)
    }));
  };

  const refreshProfile = () => {
    if (user) {
      fetchProfileStats(user.username, user.role);
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      token,
      profileStats,
      loading,
      login,
      register,
      quickSwitchUser,
      changePassword,
      logout,
      updateRole,
      updateXpPoints,
      refreshProfile,
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
