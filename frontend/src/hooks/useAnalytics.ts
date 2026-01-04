import { useQuery } from '@tanstack/react-query';
import { analyticsApi } from '../services/api';

export const useDashboardStats = () => {
  return useQuery({
    queryKey: ['analytics', 'dashboard'],
    queryFn: () => analyticsApi.getDashboardStats(),
  });
};

export const useTrends = (days: number = 30) => {
  return useQuery({
    queryKey: ['analytics', 'trends', days],
    queryFn: () => analyticsApi.getTrends(days),
  });
};

export const useSuccessPrediction = (projectId?: string) => {
  return useQuery({
    queryKey: ['analytics', 'prediction', projectId],
    queryFn: () => analyticsApi.predictSuccessRate(projectId),
    enabled: !!projectId,
  });
};

export const useBottlenecks = () => {
  return useQuery({
    queryKey: ['analytics', 'bottlenecks'],
    queryFn: () => analyticsApi.identifyBottlenecks(),
  });
};
