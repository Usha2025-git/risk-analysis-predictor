import { useRisks } from '../hooks/useRisks';
import LoadingSpinner from '../components/common/LoadingSpinner';

export default function RiskAnalysis() {
  const { data: risks, isLoading } = useRisks();

  if (isLoading) return <LoadingSpinner />;

  const severityCounts = {
    critical: risks?.filter((r) => r.severity === 'critical').length || 0,
    high: risks?.filter((r) => r.severity === 'high').length || 0,
    medium: risks?.filter((r) => r.severity === 'medium').length || 0,
    low: risks?.filter((r) => r.severity === 'low').length || 0,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-gray-900">Risk Analysis</h1>
        <p className="text-gray-600 mt-2">Identify and manage project risks</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-red-50 rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">Critical Risks</p>
          <p className="text-3xl font-bold text-red-600">{severityCounts.critical}</p>
        </div>
        <div className="bg-orange-50 rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">High Risks</p>
          <p className="text-3xl font-bold text-orange-600">{severityCounts.high}</p>
        </div>
        <div className="bg-yellow-50 rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">Medium Risks</p>
          <p className="text-3xl font-bold text-yellow-600">{severityCounts.medium}</p>
        </div>
        <div className="bg-green-50 rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">Low Risks</p>
          <p className="text-3xl font-bold text-green-600">{severityCounts.low}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Risk Register</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b">
              <tr>
                <th className="px-4 py-2 text-left font-semibold text-gray-900">Title</th>
                <th className="px-4 py-2 text-left font-semibold text-gray-900">Category</th>
                <th className="px-4 py-2 text-left font-semibold text-gray-900">Severity</th>
                <th className="px-4 py-2 text-left font-semibold text-gray-900">Score</th>
                <th className="px-4 py-2 text-left font-semibold text-gray-900">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {risks?.map((risk) => (
                <tr key={risk.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">{risk.title}</td>
                  <td className="px-4 py-3 capitalize">{risk.category}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        risk.severity === 'critical'
                          ? 'bg-red-100 text-red-800'
                          : risk.severity === 'high'
                          ? 'bg-orange-100 text-orange-800'
                          : risk.severity === 'medium'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {risk.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-semibold">{risk.risk_score.toFixed(2)}</td>
                  <td className="px-4 py-3 capitalize">{risk.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
