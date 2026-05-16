import { useState, useEffect } from 'react';
import { authApi } from '../api/auth';
import { User } from '../types';

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const userData = await authApi.getCurrentUser();
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      // Токен недействителен
      authApi.logout();
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (login: string, password: string) => {
    const response = await authApi.login({ login, password });
    localStorage.setItem('access_token', response.access_token);
    setIsAuthenticated(true);
    await checkAuth();
    return response;
  };

  const logout = () => {
    authApi.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  return {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    checkAuth,
  };
};
