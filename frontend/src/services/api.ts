import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { LoginRequest, RegisterRequest, AuthResponse, User, Project, Risk, Resource, DashboardStats, AnalyticsResponse, CreateProjectRequest, CreateRiskRequest } from '../types';

type QueryParams = Record<string, string | number | boolean | undefined>;

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to attach JWT token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API calls
export const authApi = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);
    
    const response = await apiClient.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },
};

// Project API calls
export const projectApi = {
  create: async (project: CreateProjectRequest): Promise<Project> => {
    const response = await apiClient.post<Project>('/projects', project);
    return response.data;
  },

  list: async (skip: number = 0, limit: number = 100, status?: string): Promise<Project[]> => {
    const params: QueryParams = { skip, limit };
    if (status) params.status = status;
    const response = await apiClient.get<Project[]>('/projects', { params });
    return response.data;
  },

  get: async (projectId: string): Promise<Project> => {
    const response = await apiClient.get<Project>(`/projects/${projectId}`);
    return response.data;
  },

  update: async (projectId: string, project: Partial<Project>): Promise<Project> => {
    const response = await apiClient.put<Project>(`/projects/${projectId}`, project);
    return response.data;
  },

  delete: async (projectId: string): Promise<{ detail: string }> => {
    const response = await apiClient.delete<{ detail: string }>(`/projects/${projectId}`);
    return response.data;
  },

  analyze: async (projectId: string): Promise<Record<string, unknown>> => {
    const response = await apiClient.post(`/projects/${projectId}/analyze`);
    return response.data as Record<string, unknown>;
  },
};

// Risk API calls
export const riskApi = {
  create: async (risk: CreateRiskRequest): Promise<Risk> => {
    const response = await apiClient.post<Risk>('/risks', risk);
    return response.data;
  },

  list: async (skip: number = 0, limit: number = 100, projectId?: string, severity?: string): Promise<Risk[]> => {
    const params: QueryParams = { skip, limit };
    if (projectId) params.project_id = projectId;
    if (severity) params.severity = severity;
    const response = await apiClient.get<Risk[]>('/risks', { params });
    return response.data;
  },

  get: async (riskId: string): Promise<Risk> => {
    const response = await apiClient.get<Risk>(`/risks/${riskId}`);
    return response.data;
  },

  update: async (riskId: string, risk: Partial<Risk>): Promise<Risk> => {
    const response = await apiClient.put<Risk>(`/risks/${riskId}`, risk);
    return response.data;
  },

  delete: async (riskId: string): Promise<{ detail: string }> => {
    const response = await apiClient.delete<{ detail: string }>(`/risks/${riskId}`);
    return response.data;
  },
};

// Resource API calls
export const resourceApi = {
  create: async (resource: Partial<Resource>): Promise<Resource> => {
    const response = await apiClient.post<Resource>('/resources', resource);
    return response.data;
  },

  list: async (skip: number = 0, limit: number = 100, skillCategory?: string, status?: string): Promise<Resource[]> => {
    const params: QueryParams = { skip, limit };
    if (skillCategory) params.skill_category = skillCategory;
    if (status) params.status = status;
    const response = await apiClient.get<Resource[]>('/resources', { params });
    return response.data;
  },

  get: async (resourceId: string): Promise<Resource> => {
    const response = await apiClient.get<Resource>(`/resources/${resourceId}`);
    return response.data;
  },

  update: async (resourceId: string, resource: Partial<Resource>): Promise<Resource> => {
    const response = await apiClient.put<Resource>(`/resources/${resourceId}`, resource);
    return response.data;
  },

  delete: async (resourceId: string): Promise<{ detail: string }> => {
    const response = await apiClient.delete<{ detail: string }>(`/resources/${resourceId}`);
    return response.data;
  },

  allocate: async (resourceId: string, allocation: number): Promise<Record<string, unknown>> => {
    const response = await apiClient.post(`/resources/${resourceId}/allocate`, { allocation });
    return response.data as Record<string, unknown>;
  },
};

// Analytics API calls
export const analyticsApi = {
  getDashboardStats: async (): Promise<DashboardStats> => {
    const response = await apiClient.get<DashboardStats>('/analytics/dashboard');
    return response.data;
  },

  getTrends: async (days: number = 30): Promise<AnalyticsResponse> => {
    const response = await apiClient.get<AnalyticsResponse>('/analytics/trends', { params: { days } });
    return response.data;
  },

  predictSuccessRate: async (projectId?: string): Promise<AnalyticsResponse | Record<string, unknown>> => {
    const params: QueryParams = projectId ? { project_id: projectId } : {};
    const response = await apiClient.get<Record<string, unknown>>('/analytics/predictions/success-rate', { params });
    return response.data as Record<string, unknown>;
  },

  identifyBottlenecks: async (): Promise<Record<string, unknown>> => {
    const response = await apiClient.get<Record<string, unknown>>('/analytics/bottlenecks');
    return response.data as Record<string, unknown>;
  },
};

export default apiClient;
