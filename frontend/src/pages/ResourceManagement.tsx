import { useResources } from '../hooks/useResources';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { formatCurrency, formatPercentage } from '../utils/formatters';

export default function ResourceManagement() {
  const { data: resources, isLoading } = useResources();

  if (isLoading) return <LoadingSpinner />;

  const availableCount = resources?.filter((r) => r.status === 'available').length || 0;
  const onLeaveCount = resources?.filter((r) => r.status === 'on_leave').length || 0;
  const unavailableCount = resources?.filter((r) => r.status === 'unavailable').length || 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-gray-900">Resource Management</h1>
        <p className="text-gray-600 mt-2">Manage team members and allocations</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-green-50 rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">Available</p>
          <p className="text-3xl font-bold text-green-600">{availableCount}</p>
        </div>
        <div className="bg-yellow-50 rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">On Leave</p>
          <p className="text-3xl font-bold text-yellow-600">{onLeaveCount}</p>
        </div>
        <div className="bg-red-50 rounded-lg shadow p-6">
          <p className="text-gray-600 text-sm">Unavailable</p>
          <p className="text-3xl font-bold text-red-600">{unavailableCount}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Team Resources</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="border-b">
              <tr>
                <th className="px-4 py-2 text-left font-semibold text-gray-900">Name</th>
                <th className="px-4 py-2 text-left font-semibold text-gray-900">Skill Level</th>
                <th className="px-4 py-2 text-left font-semibold text-gray-900">Allocation</th>
                <th className="px-4 py-2 text-left font-semibold text-gray-900">Hourly Rate</th>
                <th className="px-4 py-2 text-left font-semibold text-gray-900">Status</th>
                <th className="px-4 py-2 text-left font-semibold text-gray-900">Productivity</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {resources?.map((resource) => (
                <tr key={resource.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium">{resource.name}</td>
                  <td className="px-4 py-3 capitalize">{resource.skill_level}</td>
                  <td className="px-4 py-3">{formatPercentage(resource.current_allocation)}</td>
                  <td className="px-4 py-3">{formatCurrency(resource.hourly_rate)}/hr</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        resource.status === 'available'
                          ? 'bg-green-100 text-green-800'
                          : resource.status === 'on_leave'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {resource.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">{formatPercentage(resource.productivity_score)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
