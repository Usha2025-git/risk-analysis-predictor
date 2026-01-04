/**
 * API and domain types for the Risk Analysis Predictor
 */

export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled';
  start_date: string;
  planned_end_date: string;
  actual_end_date?: string;
  team_size: number;
  manager: string;
  budget: number;
  actual_cost: number;
  risk_level: 'low' | 'medium' | 'high';
  health_score: number;
  success_probability: number;
  created_at: string;
  updated_at: string;
}

export interface Risk {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  category: 'technical' | 'resource' | 'schedule' | 'financial' | 'external' | 'other';
  severity: 'low' | 'medium' | 'high' | 'critical';
  probability: number;
  impact: number;
  risk_score: number;
  status: 'identified' | 'mitigating' | 'mitigated' | 'occurred';
  mitigation_strategy?: string;
  mitigation_owner?: string;
  mitigation_deadline?: string;
  incident_frequency: number;
  created_at: string;
  updated_at: string;
}

export interface Resource {
  id: string;
  name: string;
  email: string;
  skill_category: string;
  skill_level: 'junior' | 'mid' | 'senior' | 'expert';
  current_allocation: number;
  max_allocation: number;
  hourly_rate: number;
  status: 'available' | 'on_leave' | 'unavailable';
  availability_start?: string;
  availability_end?: string;
  productivity_score: number;
  quality_score: number;
  created_at: string;
  updated_at: string;
}

export interface Bottleneck {
  type: string;
  resource_id?: string;
  resource_name?: string;
  project_id?: string;
  project_name?: string;
  current?: number;
  max?: number;
  required?: number;
  assigned?: number;
  productivity_score?: number;
  severity: 'low' | 'medium' | 'high';
}

export interface DashboardStats {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  average_health_score: number;
  average_success_probability: number;
  high_risk_projects: number;
  critical_risks: number;
  total_resources: number;
  average_resource_utilization: number;
  overall_risk_score: number;
}

export interface AnalyticsResponse {
  time_period: string;
  projects_created: number;
  projects_completed: number;
  success_rate: number;
  risks_identified: number;
  high_severity_risks: number;
  average_risk_score: number;
  total_data_points: number;
  recommendations: string[];
}

export interface ApiResponse<T> {
  data: T;
  message: string;
  status: 'success' | 'error';
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  start_date: string;
  planned_end_date: string;
  team_size: number;
  manager: string;
  budget: number;
  risk_level: 'low' | 'medium' | 'high';
}

export interface CreateRiskRequest {
  project_id: string;
  title: string;
  description?: string;
  category: 'technical' | 'resource' | 'schedule' | 'financial' | 'external' | 'other';
  severity: 'low' | 'medium' | 'high' | 'critical';
  probability: number;
  impact: number;
}

export interface WebSocketMessage {
  type: 'subscribe' | 'unsubscribe' | 'message';
  event_type?: string;
  data?: unknown;
  client_id?: string;
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
}
