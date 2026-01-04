import { useState } from 'react';
import { useProjects, useCreateProject, useDeleteProject } from '../hooks/useProjects';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { formatDate, formatCurrency, formatPercentage } from '../utils/formatters';
import { PROJECT_STATUSES, RISK_LEVELS } from '../utils/constants';
import { CreateProjectRequest } from '../types';
import { motion } from 'framer-motion';
import { Plus, Search, Trash2, Eye } from 'lucide-react';

export default function Projects() {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);

  const { data: projects, isLoading } = useProjects();
  const createProjectMutation = useCreateProject();
  const deleteProjectMutation = useDeleteProject();

  const [formData, setFormData] = useState<CreateProjectRequest>({
    name: '',
    description: '',
    start_date: '',
    planned_end_date: '',
    team_size: 5,
    manager: '',
    budget: 0,
    risk_level: 'medium',
  });

  const filteredProjects = (projects || []).filter((project) => {
    const matchesSearch =
      project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = !statusFilter || project.status === statusFilter;
    const matchesRisk = !riskFilter || project.risk_level === riskFilter;
    return matchesSearch && matchesStatus && matchesRisk;
  });

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createProjectMutation.mutateAsync(formData);
      setFormData({
        name: '',
        description: '',
        start_date: '',
        planned_end_date: '',
        team_size: 5,
        manager: '',
        budget: 0,
        risk_level: 'medium',
      });
      setShowCreateForm(false);
    } catch (error) {
      // Error is handled by the hook
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      await deleteProjectMutation.mutateAsync(projectId);
    }
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Projects</h1>
          <p className="text-gray-600 mt-2">Manage and monitor all your projects</p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center space-x-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus size={20} />
          <span>New Project</span>
        </button>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <motion.form
          onSubmit={handleCreateProject}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-lg shadow p-6 space-y-4"
        >
          <h2 className="text-xl font-semibold text-gray-900">Create New Project</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Project Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
            />
            <input
              type="text"
              placeholder="Project Manager"
              value={formData.manager}
              onChange={(e) => setFormData({ ...formData, manager: e.target.value })}
              required
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
            />
            <input
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              aria-label="Project start date"
              title="Project start date"
              required
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
            />
            <input
              type="date"
              value={formData.planned_end_date}
              onChange={(e) => setFormData({ ...formData, planned_end_date: e.target.value })}
              aria-label="Planned end date"
              title="Planned end date"
              required
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
            />
            <input
              type="number"
              placeholder="Budget"
              value={formData.budget}
              onChange={(e) => setFormData({ ...formData, budget: parseFloat(e.target.value) || 0 })}
              required
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
            />
            <input
              type="number"
              placeholder="Team Size"
              value={formData.team_size}
              onChange={(e) => setFormData({ ...formData, team_size: parseInt(e.target.value, 10) || 0 })}
              required
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
            />
          </div>
          
          <textarea
            placeholder="Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
            rows={3}
          />
          
          <select
            value={formData.risk_level}
            onChange={(e) =>
              setFormData({
                ...formData,
                risk_level: e.target.value as CreateProjectRequest['risk_level'],
              })
            }
            aria-label="Project risk level"
            title="Project risk level"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
          >
            <option value="low">Low Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="high">High Risk</option>
          </select>
          
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={createProjectMutation.isPending}
              className="flex-1 bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
            >
              {createProjectMutation.isPending ? 'Creating...' : 'Create Project'}
            </button>
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 transition-colors"
            >
              Cancel
            </button>
          </div>
        </motion.form>
      )}

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4 space-y-4">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search projects..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            aria-label="Filter projects by status"
            title="Filter projects by status"
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
          >
            <option value="">All Statuses</option>
            {PROJECT_STATUSES.map((status) => (
              <option key={status.value} value={status.value}>
                {status.label}
              </option>
            ))}
          </select>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            aria-label="Filter projects by risk"
            title="Filter projects by risk"
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
          >
            <option value="">All Risks</option>
            {RISK_LEVELS.map((level) => (
              <option key={level.value} value={level.value}>
                {level.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProjects.map((project, index) => {
          const statusBadge = PROJECT_STATUSES.find((s) => s.value === project.status);
          const riskBadge = RISK_LEVELS.find((r) => r.value === project.risk_level);

          return (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow overflow-hidden"
            >
              <div className="p-6 space-y-4">
                {/* Header */}
                <div className="flex items-start justify-between">
                  <h3 className="text-lg font-semibold text-gray-900 flex-1">{project.name}</h3>
                  <button
                    onClick={() => handleDeleteProject(project.id)}
                    aria-label={`Delete project ${project.name}`}
                    title={`Delete project ${project.name}`}
                    className="text-red-500 hover:text-red-700 transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>

                {/* Description */}
                {project.description && (
                  <p className="text-sm text-gray-600 line-clamp-2">{project.description}</p>
                )}

                {/* Badges */}
                <div className="flex gap-2">
                  {statusBadge && (
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusBadge.color}`}>
                      {statusBadge.label}
                    </span>
                  )}
                  {riskBadge && (
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${riskBadge.color}`}>
                      {riskBadge.label}
                    </span>
                  )}
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-gray-600">Budget</p>
                    <p className="font-semibold text-gray-900">{formatCurrency(project.budget)}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Team Size</p>
                    <p className="font-semibold text-gray-900">{project.team_size}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Health Score</p>
                    <p className="font-semibold text-gray-900">{formatPercentage(project.health_score)}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Success Rate</p>
                    <p className="font-semibold text-gray-900">
                      {formatPercentage(project.success_probability)}
                    </p>
                  </div>
                </div>

                {/* Dates */}
                <div className="text-xs text-gray-500 space-y-1">
                  <p>Start: {formatDate(project.start_date)}</p>
                  <p>End: {formatDate(project.planned_end_date)}</p>
                </div>

                {/* View Button */}
                <button
                  onClick={() => navigate(`/projects/${project.id}`)}
                  className="w-full flex items-center justify-center space-x-2 bg-primary-600 text-white py-2 rounded-lg hover:bg-primary-700 transition-colors"
                >
                  <Eye size={16} />
                  <span>View Details</span>
                </button>
              </div>
            </motion.div>
          );
        })}
      </div>

      {filteredProjects.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No projects found</p>
          <p className="text-gray-400 text-sm">Create a new project to get started</p>
        </div>
      )}
    </div>
  );
}
