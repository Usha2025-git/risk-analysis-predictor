import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { isAxiosError } from 'axios';
import { riskApi } from '../services/api';
import { useNotificationStore } from '../store/notificationStore';
import { Risk, CreateRiskRequest } from '../types';

const getErrorMessage = (error: unknown): string => {
  if (isAxiosError(error)) {
    return error.response?.data?.detail ?? error.message;
  }
  if (error instanceof Error) return error.message;
  return 'Request failed';
};

export const useRisks = (skip: number = 0, limit: number = 100, projectId?: string, severity?: string) => {
  return useQuery({
    queryKey: ['risks', skip, limit, projectId, severity],
    queryFn: () => riskApi.list(skip, limit, projectId, severity),
  });
};

export const useRisk = (riskId: string) => {
  return useQuery({
    queryKey: ['risk', riskId],
    queryFn: () => riskApi.get(riskId),
    enabled: !!riskId,
  });
};

export const useCreateRisk = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (risk: CreateRiskRequest) => riskApi.create(risk),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] });
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Risk identified successfully',
      });
    },
    onError: (error) => {
      const message = getErrorMessage(error) || 'Failed to create risk';
      addNotification({
        type: 'error',
        title: 'Error',
        message,
      });
    },
  });
};

export const useUpdateRisk = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: ({ riskId, data }: { riskId: string; data: Partial<Risk> }) =>
      riskApi.update(riskId, data),
    onSuccess: (updatedRisk) => {
      queryClient.invalidateQueries({ queryKey: ['risks'] });
      queryClient.invalidateQueries({ queryKey: ['risk', updatedRisk.id] });
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Risk updated successfully',
      });
    },
    onError: (error) => {
      const message = getErrorMessage(error) || 'Failed to update risk';
      addNotification({
        type: 'error',
        title: 'Error',
        message,
      });
    },
  });
};

export const useDeleteRisk = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (riskId: string) => riskApi.delete(riskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['risks'] });
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Risk deleted successfully',
      });
    },
    onError: (error) => {
      const message = getErrorMessage(error) || 'Failed to delete risk';
      addNotification({
        type: 'error',
        title: 'Error',
        message,
      });
    },
  });
};
