import { useProject } from '../hooks/useProjects';
import { useParams } from 'react-router-dom';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { formatDate, formatCurrency, formatPercentage } from '../utils/formatters';

export default function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const { data: project, isLoading } = useProject(projectId || '');

  if (isLoading) return <LoadingSpinner />;
  if (!project) return <div className="text-center text-gray-500">Project not found</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-gray-900">{project.name}</h1>
        <p className="text-gray-600 mt-2">{project.description}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-2xl font-semibold text-gray-900">Project Details</h2>
          <dl className="grid grid-cols-2 gap-4">
            <div>
              <dt className="text-sm text-gray-600">Status</dt>
              <dd className="text-lg font-semibold text-gray-900 capitalize">{project.status}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-600">Risk Level</dt>
              <dd className="text-lg font-semibold text-gray-900 capitalize">{project.risk_level}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-600">Manager</dt>
              <dd className="text-lg font-semibold text-gray-900">{project.manager}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-600">Team Size</dt>
              <dd className="text-lg font-semibold text-gray-900">{project.team_size}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-600">Start Date</dt>
              <dd className="text-lg font-semibold text-gray-900">{formatDate(project.start_date)}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-600">Planned End</dt>
              <dd className="text-lg font-semibold text-gray-900">
                {formatDate(project.planned_end_date)}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-gray-600">Budget</dt>
              <dd className="text-lg font-semibold text-gray-900">{formatCurrency(project.budget)}</dd>
            </div>
            <div>
              <dt className="text-sm text-gray-600">Actual Cost</dt>
              <dd className="text-lg font-semibold text-gray-900">{formatCurrency(project.actual_cost)}</dd>
            </div>
          </dl>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Health Metrics</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Health Score</p>
                <p className="text-2xl font-bold text-primary-600">
                  {formatPercentage(project.health_score)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Success Probability</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatPercentage(project.success_probability)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
