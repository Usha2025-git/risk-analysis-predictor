import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { isAxiosError } from 'axios';
import { projectApi } from '../services/api';
import { useProjectStore } from '../store/projectStore';
import { useNotificationStore } from '../store/notificationStore';
import { Project, CreateProjectRequest } from '../types';

const getErrorMessage = (error: unknown): string => {
  if (isAxiosError(error)) {
    return error.response?.data?.detail ?? error.message;
  }
  if (error instanceof Error) return error.message;
  return 'Request failed';
};

export const useProjects = (skip: number = 0, limit: number = 100, status?: string) => {
  const { setProjects, setIsLoading, setError } = useProjectStore();
  const { addNotification } = useNotificationStore();

  return useQuery({
    queryKey: ['projects', skip, limit, status],
    queryFn: async () => {
      setIsLoading(true);
      try {
        const data = await projectApi.list(skip, limit, status);
        setProjects(data);
        setIsLoading(false);
        return data;
      } catch (error) {
        const message = getErrorMessage(error) || 'Failed to load projects';
        setError(message);
        addNotification({
          type: 'error',
          title: 'Error',
          message,
        });
        setIsLoading(false);
        throw error;
      }
    },
  });
};

export const useProject = (projectId: string) => {
  return useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectApi.get(projectId),
    enabled: !!projectId,
  });
};

export const useCreateProject = () => {
  const queryClient = useQueryClient();
  const { addProject } = useProjectStore();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (project: CreateProjectRequest) => projectApi.create(project),
    onSuccess: (newProject) => {
      addProject(newProject);
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Project created successfully',
      });
    },
    onError: (error) => {
      const message = getErrorMessage(error) || 'Failed to create project';
      addNotification({
        type: 'error',
        title: 'Error',
        message,
      });
    },
  });
};

export const useUpdateProject = () => {
  const queryClient = useQueryClient();
  const { updateProject } = useProjectStore();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: Partial<Project> }) =>
      projectApi.update(projectId, data),
    onSuccess: (updatedProject) => {
      updateProject(updatedProject);
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      queryClient.invalidateQueries({ queryKey: ['project', updatedProject.id] });
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Project updated successfully',
      });
    },
    onError: (error) => {
      const message = getErrorMessage(error) || 'Failed to update project';
      addNotification({
        type: 'error',
        title: 'Error',
        message,
      });
    },
  });
};

export const useDeleteProject = () => {
  const queryClient = useQueryClient();
  const { removeProject } = useProjectStore();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (projectId: string) => projectApi.delete(projectId),
    onSuccess: (_, projectId) => {
      removeProject(projectId);
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Project deleted successfully',
      });
    },
    onError: (error) => {
      const message = getErrorMessage(error) || 'Failed to delete project';
      addNotification({
        type: 'error',
        title: 'Error',
        message,
      });
    },
  });
};

export const useAnalyzeProject = () => {
  const queryClient = useQueryClient();
  const { addNotification } = useNotificationStore();

  return useMutation({
    mutationFn: (projectId: string) => projectApi.analyze(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['project'] });
      addNotification({
        type: 'success',
        title: 'Analysis Complete',
        message: 'Project analysis has been completed',
      });
    },
    onError: (error: unknown) => {
      const message = getErrorMessage(error) || 'Failed to analyze project';
      addNotification({
        type: 'error',
        title: 'Error',
        message,
      });
    },
  });
};
