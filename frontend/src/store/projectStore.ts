import { create } from 'zustand';
import { Project } from '../types';

interface ProjectState {
  projects: Project[];
  selectedProject: Project | null;
  filters: {
    status?: string;
    riskLevel?: string;
    searchTerm?: string;
  };
  isLoading: boolean;
  error: string | null;

  // Actions
  setProjects: (projects: Project[]) => void;
  setSelectedProject: (project: Project | null) => void;
  setFilters: (filters: Partial<ProjectState['filters']>) => void;
  setIsLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  
  addProject: (project: Project) => void;
  updateProject: (project: Project) => void;
  removeProject: (projectId: string) => void;
  
  getFilteredProjects: () => Project[];
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  selectedProject: null,
  filters: {},
  isLoading: false,
  error: null,

  setProjects: (projects) => set({ projects }),
  setSelectedProject: (project) => set({ selectedProject: project }),
  setFilters: (filters) => set((state) => ({
    filters: { ...state.filters, ...filters },
  })),
  setIsLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),

  addProject: (project) => set((state) => ({
    projects: [...state.projects, project],
  })),

  updateProject: (project) => set((state) => ({
    projects: state.projects.map((p) => p.id === project.id ? project : p),
  })),

  removeProject: (projectId) => set((state) => ({
    projects: state.projects.filter((p) => p.id !== projectId),
  })),

  getFilteredProjects: () => {
    const state = get();
    let filtered = state.projects;

    if (state.filters.status) {
      filtered = filtered.filter((p) => p.status === state.filters.status);
    }

    if (state.filters.riskLevel) {
      filtered = filtered.filter((p) => p.risk_level === state.filters.riskLevel);
    }

    if (state.filters.searchTerm) {
      const term = state.filters.searchTerm.toLowerCase();
      filtered = filtered.filter((p) =>
        p.name.toLowerCase().includes(term) || p.description?.toLowerCase().includes(term)
      );
    }

    return filtered;
  },
}));
