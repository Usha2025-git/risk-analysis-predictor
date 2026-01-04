import { create } from 'zustand';
import { User } from '../types';
import { authApi } from '../services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;

  // Actions
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setIsLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  
  login: (email: string, password: string) => Promise<void>;
  loginDemo: () => Promise<void>;
  register: (email: string, username: string, password: string) => Promise<void>;
  logout: () => void;
  getCurrentUser: () => Promise<void>;
  hydrate: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isLoading: false,
  error: null,
  isAuthenticated: false,

  setUser: (user) => set({ user, isAuthenticated: !!user }),
  setToken: (token) => set({ token }),
  setIsLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authApi.login({ email, password });
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      set({
        user: response.user,
        token: response.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error: unknown) {
      let message = 'Login failed';
      if (typeof error === 'object' && error !== null && 'response' in error) {
        const err = error as { response?: { data?: { detail?: string } } };
        message = err.response?.data?.detail || 'Login failed';
      }
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  loginDemo: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await authApi.demoLogin();
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      set({
        user: response.user,
        token: response.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error: unknown) {
      let message = 'Demo login failed';
      if (typeof error === 'object' && error !== null && 'response' in error) {
        const err = error as { response?: { data?: { detail?: string } } };
        message = err.response?.data?.detail || 'Demo login failed';
      }
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  register: async (email, username, password) => {
    set({ isLoading: true, error: null });
    try {
      const response = await authApi.register({ email, username, password });
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      set({
        user: response.user,
        token: response.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error: unknown) {
      let message = 'Registration failed';
      if (typeof error === 'object' && error !== null && 'response' in error) {
        const err = error as { response?: { data?: { detail?: string } } };
        message = err.response?.data?.detail || 'Registration failed';
      }
      set({ error: message, isLoading: false });
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },

  getCurrentUser: async () => {
    set({ isLoading: true });
    try {
      const user = await authApi.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isAuthenticated: false, isLoading: false });
    }
  },

  hydrate: () => {
    const token = localStorage.getItem('access_token');
    const userStr = localStorage.getItem('user');
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        set({
          token,
          user,
          isAuthenticated: true,
        });
      } catch {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    }
  },
}));
