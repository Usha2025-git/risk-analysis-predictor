import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { isAxiosError } from 'axios';
import { resourceApi } from '../services/api';
import { useNotificationStore } from '../store/notificationStore';
import { Resource } from '../types';

const getErrorMessage = (error: unknown): string => {
  if (isAxiosError(error)) {
    return error.response?.data?.detail ?? error.message;
  }
  if (error instanceof Error) return error.message;
  return 'Request failed';
};

export const useResources = (skip: number = 0, limit: number = 100, skillCategory?: string, status?: string) => {
  return useQuery({
    queryKey: ['resources', skip, limit, skillCategory, status],
    queryFn: () => resourceApi.list(skip, limit, skillCategory, status),
  });
};

export const useResource = (resourceId: string) => {
  return useQuery({
    queryKey: ['resource', resourceId],
    queryFn: () => resourceApi.get(resourceId),
    enabled: !!resourceId,
  });
};

export const useCreateResource = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (resource: Partial<Resource>) => resourceApi.create(resource),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Resource added successfully',
      });
    },
    onError: (error) => {
      const message = getErrorMessage(error) || 'Failed to add resource';
      addNotification({
        type: 'error',
        title: 'Error',
        message,
      });
    },
  });
};

export const useUpdateResource = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: ({ resourceId, data }: { resourceId: string; data: Partial<Resource> }) =>
      resourceApi.update(resourceId, data),
    onSuccess: (updatedResource) => {
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      queryClient.invalidateQueries({ queryKey: ['resource', updatedResource.id] });
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Resource updated successfully',
      });
    },
    onError: (error) => {
      const message = getErrorMessage(error) || 'Failed to update resource';
      addNotification({
        type: 'error',
        title: 'Error',
        message,
      });
    },
  });
};

export const useDeleteResource = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (resourceId: string) => resourceApi.delete(resourceId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Resource deleted successfully',
      });
    },
    onError: (error) => {
      const message = getErrorMessage(error) || 'Failed to delete resource';
      addNotification({
        type: 'error',
        title: 'Error',
        message,
      });
    },
  });
};

export const useAllocateResource = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: ({ resourceId, allocation }: { resourceId: string; allocation: number }) =>
      resourceApi.allocate(resourceId, allocation),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resources'] });
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Resource allocated successfully',
      });
    },
    onError: (error) => {
      const message = getErrorMessage(error) || 'Failed to allocate resource';
      addNotification({
        type: 'error',
        title: 'Error',
        message,
      });
    },
  });
};
