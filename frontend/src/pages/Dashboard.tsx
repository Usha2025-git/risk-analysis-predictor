import { useEffect, useState } from 'react';
import { useDashboardStats, useTrends, useBottlenecks } from '../hooks/useAnalytics';
import { useProjects } from '../hooks/useProjects';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { TrendingUp, AlertTriangle, Users, CheckCircle, Clock } from 'lucide-react';
import { Bottleneck } from '../types';

type ChartDatum = { name: string; value: number; fill: string };

interface BottleneckResponse {
  bottleneck_count: number;
  bottlenecks: Bottleneck[];
}

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: trends, isLoading: trendsLoading } = useTrends();
  const { data: bottlenecksRaw, isLoading: bottlenecksLoading } = useBottlenecks();
  const { data: projects } = useProjects();

  const [statusData, setStatusData] = useState<ChartDatum[]>([]);
  const [riskData, setRiskData] = useState<ChartDatum[]>([]);

  // Type-guard the bottlenecks response
  const bottlenecks = bottlenecksRaw && typeof bottlenecksRaw === 'object' && 'bottleneck_count' in bottlenecksRaw
    ? (bottlenecksRaw as unknown as BottleneckResponse)
    : undefined;

  useEffect(() => {
    if (projects) {
      const statusCounts = {
        planning: projects.filter((p) => p.status === 'planning').length,
        active: projects.filter((p) => p.status === 'active').length,
        on_hold: projects.filter((p) => p.status === 'on_hold').length,
        completed: projects.filter((p) => p.status === 'completed').length,
      };

      setStatusData([
        { name: 'Planning', value: statusCounts.planning, fill: '#3b82f6' },
        { name: 'Active', value: statusCounts.active, fill: '#10b981' },
        { name: 'On Hold', value: statusCounts.on_hold, fill: '#f59e0b' },
        { name: 'Completed', value: statusCounts.completed, fill: '#8b5cf6' },
      ]);

      const riskCounts = {
        low: projects.filter((p) => p.risk_level === 'low').length,
        medium: projects.filter((p) => p.risk_level === 'medium').length,
        high: projects.filter((p) => p.risk_level === 'high').length,
      };

      setRiskData([
        { name: 'Low Risk', value: riskCounts.low, fill: '#10b981' },
        { name: 'Medium Risk', value: riskCounts.medium, fill: '#f59e0b' },
        { name: 'High Risk', value: riskCounts.high, fill: '#ef4444' },
      ]);
    }
  }, [projects]);

  if (statsLoading || trendsLoading || bottlenecksLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Overview of your projects, risks, and resources</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Total Projects</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_projects ?? 0}</p>
            </div>
            <CheckCircle className="text-primary-500" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Active Projects</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.active_projects ?? 0}</p>
            </div>
            <TrendingUp className="text-green-500" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Critical Risks</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.critical_risks ?? 0}</p>
            </div>
            <AlertTriangle className="text-red-500" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Resources</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.total_resources ?? 0}</p>
            </div>
            <Users className="text-blue-500" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-600 text-sm">Avg Health Score</p>
              <p className="text-3xl font-bold text-gray-900">
                {stats?.average_health_score ? `${(stats.average_health_score * 100).toFixed(0)}%` : '0%'}
              </p>
            </div>
            <Clock className="text-purple-500" size={32} />
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Project Status Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Project Status Distribution</h2>
          {statusData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-8">No project data available</p>
          )}
        </div>

        {/* Risk Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h2>
          {riskData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 text-center py-8">No risk data available</p>
          )}
        </div>
      </div>

      {/* Trends and Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Success Trends</h2>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-gray-600 text-sm">Projects Created</p>
              <p className="text-2xl font-bold text-gray-900">{trends?.projects_created ?? 0}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Completed</p>
              <p className="text-2xl font-bold text-green-600">{trends?.projects_completed ?? 0}</p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Success Rate</p>
              <p className="text-2xl font-bold text-primary-600">
                {trends?.success_rate ? `${trends.success_rate.toFixed(1)}%` : '0%'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Resource Utilization</h2>
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-2">Average Allocation</p>
            <p className="text-3xl font-bold text-primary-600">
              {stats?.average_resource_utilization ? `${stats.average_resource_utilization.toFixed(1)}%` : '0%'}
            </p>
          </div>
        </div>
      </div>

      {/* Bottlenecks Alert */}
      {bottlenecks && bottlenecks.bottleneck_count > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-900 mb-4">
            Active Bottlenecks ({bottlenecks.bottleneck_count})
          </h2>
          <div className="space-y-3">
            {bottlenecks.bottlenecks?.slice(0, 5).map((bottleneck: Bottleneck, idx: number) => (
              <div key={idx} className="flex items-start space-x-3 pb-3 border-b border-red-200 last:border-0">
                <AlertTriangle className="text-red-500 flex-shrink-0 mt-1" size={20} />
                <div className="flex-1">
                  <p className="font-medium text-red-900">{bottleneck.type}</p>
                  <p className="text-sm text-red-700">
                    {bottleneck.resource_name || bottleneck.project_name || 'Resource'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
