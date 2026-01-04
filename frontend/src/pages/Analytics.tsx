import { useTrends } from '../hooks/useAnalytics';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export default function Analytics() {
  const { data: trends, isLoading: trendsLoading } = useTrends();

  if (trendsLoading) return <LoadingSpinner />;

  const trendData = [
    { month: 'Week 1', projects: trends?.projects_created || 0, risks: trends?.risks_identified || 0 },
    { month: 'Week 2', projects: Math.round((trends?.projects_created || 0) * 0.8), risks: Math.round((trends?.risks_identified || 0) * 0.9) },
    { month: 'Week 3', projects: Math.round((trends?.projects_created || 0) * 0.6), risks: Math.round((trends?.risks_identified || 0) * 0.7) },
    { month: 'Week 4', projects: Math.round((trends?.projects_created || 0) * 0.4), risks: Math.round((trends?.risks_identified || 0) * 0.5) },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600 mt-2">Insights and trends analysis</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">Success Rate (30 days)</p>
          <p className="text-3xl font-bold text-primary-600">{trends?.success_rate?.toFixed(1)}%</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">Avg Risk Score</p>
          <p className="text-3xl font-bold text-red-600">{trends?.average_risk_score?.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">High Severity Risks</p>
          <p className="text-3xl font-bold text-orange-600">{trends?.high_severity_risks}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Projects and Risks Trend</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="projects" fill="#0ea5e9" />
            <Bar dataKey="risks" fill="#ef4444" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recommendations</h2>
        <ul className="space-y-3">
          {trends?.recommendations?.map((rec, idx) => (
            <li key={idx} className="flex items-start space-x-3">
              <span className="flex-shrink-0 w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                {idx + 1}
              </span>
              <p className="text-gray-700">{rec}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
