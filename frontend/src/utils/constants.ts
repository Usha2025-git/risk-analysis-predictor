export const PROJECT_STATUSES = [
  { value: 'planning', label: 'Planning', color: 'bg-blue-100 text-blue-800' },
  { value: 'active', label: 'Active', color: 'bg-green-100 text-green-800' },
  { value: 'on_hold', label: 'On Hold', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'completed', label: 'Completed', color: 'bg-purple-100 text-purple-800' },
  { value: 'cancelled', label: 'Cancelled', color: 'bg-red-100 text-red-800' },
];

export const RISK_LEVELS = [
  { value: 'low', label: 'Low', color: 'bg-green-100 text-green-800' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'high', label: 'High', color: 'bg-red-100 text-red-800' },
];

export const RISK_SEVERITIES = [
  { value: 'low', label: 'Low', color: 'bg-green-100 text-green-800' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-800' },
  { value: 'critical', label: 'Critical', color: 'bg-red-100 text-red-800' },
];

export const RISK_CATEGORIES = [
  { value: 'technical', label: 'Technical' },
  { value: 'resource', label: 'Resource' },
  { value: 'schedule', label: 'Schedule' },
  { value: 'financial', label: 'Financial' },
  { value: 'external', label: 'External' },
  { value: 'other', label: 'Other' },
];

export const RISK_STATUSES = [
  { value: 'identified', label: 'Identified' },
  { value: 'mitigating', label: 'Mitigating' },
  { value: 'mitigated', label: 'Mitigated' },
  { value: 'occurred', label: 'Occurred' },
];

export const SKILL_LEVELS = [
  { value: 'junior', label: 'Junior' },
  { value: 'mid', label: 'Mid-level' },
  { value: 'senior', label: 'Senior' },
  { value: 'expert', label: 'Expert' },
];

export const RESOURCE_STATUSES = [
  { value: 'available', label: 'Available', color: 'bg-green-100 text-green-800' },
  { value: 'on_leave', label: 'On Leave', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'unavailable', label: 'Unavailable', color: 'bg-red-100 text-red-800' },
];

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const NOTIFICATION_DURATION = 5000; // ms

export const PAGE_LIMIT = 20;

export const CHART_COLORS = [
  '#0ea5e9', // primary
  '#22c55e', // success
  '#ef4444', // danger
  '#f59e0b', // warning
  '#8b5cf6', // purple
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#14b8a6', // teal
];
