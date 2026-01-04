import { useState, type KeyboardEvent } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { AlertTriangle, TrendingUp, Shield, Target, Plus } from 'lucide-react';

export default function SimpleRiskDashboard() {
  type Project = {
    id: number;
    name: string;
    risk: 'Critical' | 'High' | 'Medium' | 'Low';
    budget: number;
    progress: number;
  };

  const [projects] = useState<Project[]>([
    { id: 1, name: 'E-commerce Platform', risk: 'High', budget: 150000, progress: 65 },
    { id: 2, name: 'Mobile App Redesign', risk: 'Medium', budget: 80000, progress: 40 },
    { id: 3, name: 'Data Migration', risk: 'Critical', budget: 200000, progress: 25 },
  ]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  const riskData = [
    { name: 'Schedule Risk', value: 35, color: '#ef4444' },
    { name: 'Budget Risk', value: 25, color: '#f97316' },
    { name: 'Resource Risk', value: 20, color: '#eab308' },
    { name: 'Technical Risk', value: 20, color: '#22c55e' },
  ];

  const riskColorClasses: Record<string, string> = {
    '#ef4444': 'bg-red-500',
    '#f97316': 'bg-orange-500',
    '#eab308': 'bg-yellow-500',
    '#22c55e': 'bg-green-500',
  };

  const progressData = projects.map(p => ({
    name: p.name,
    progress: p.progress,
    budget: p.budget / 1000
  }));

  const handleProjectClick = (project: Project) => {
    setSelectedProject(project);
  };

  const handleProjectKey = (event: KeyboardEvent<HTMLDivElement>, project: Project) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      setSelectedProject(project);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'Critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'High': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="px-6 py-4">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="h-8 w-8 text-blue-600" />
            Risk Analysis & Resource Management
          </h1>
          <p className="text-gray-600 mt-1">AI-Powered Project Risk Prediction</p>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Projects</p>
                <p className="text-3xl font-bold text-gray-900">{projects.length}</p>
              </div>
              <Target className="h-12 w-12 text-blue-500 opacity-20" />
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">High Risk Projects</p>
                <p className="text-3xl font-bold text-red-600">
                  {projects.filter(p => p.risk === 'High' || p.risk === 'Critical').length}
                </p>
              </div>
              <AlertTriangle className="h-12 w-12 text-red-500 opacity-20" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Budget</p>
                <p className="text-3xl font-bold text-green-600">
                  ${projects.reduce((sum, p) => sum + p.budget, 0).toLocaleString()}
                </p>
              </div>
              <TrendingUp className="h-12 w-12 text-green-500 opacity-20" />
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Progress</p>
                <p className="text-3xl font-bold text-blue-600">
                  {Math.round(projects.reduce((sum, p) => sum + p.progress, 0) / projects.length)}%
                </p>
              </div>
              <Shield className="h-12 w-12 text-blue-500 opacity-20" />
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Distribution */}
          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-xl font-semibold mb-4">Risk Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="mt-4 grid grid-cols-2 gap-2">
              {riskData.map((risk, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded ${riskColorClasses[risk.color] ?? 'bg-gray-400'}`}></div>
                  <span className="text-sm text-gray-600">{risk.name}: {risk.value}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* Project Progress */}
          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-xl font-semibold mb-4">Project Progress</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={progressData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="progress" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Project List */}
        <div className="bg-white rounded-lg shadow border">
          <div className="px-6 py-4 border-b flex items-center justify-between">
            <h3 className="text-xl font-semibold">Active Projects</h3>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Add Project
            </button>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {projects.map((project) => (
                <div
                  key={project.id}
                  role="button"
                  tabIndex={0}
                  onClick={() => handleProjectClick(project)}
                  onKeyDown={(e) => handleProjectKey(e, project)}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label={`Open project ${project.name}`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-gray-900">{project.name}</h4>
                      <div className="flex items-center gap-4 mt-2">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getRiskColor(project.risk)}`}>
                          {project.risk} Risk
                        </span>
                        <span className="text-sm text-gray-600">
                          Budget: ${project.budget.toLocaleString()}
                        </span>
                        <span className="text-sm text-gray-600">
                          Progress: {project.progress}%
                        </span>
                      </div>
                    </div>
                    <div className="flex flex-col items-end">
                      <progress
                        value={project.progress}
                        max={100}
                        className="w-24 h-2 accent-blue-600 bg-gray-200 rounded-full overflow-hidden"
                        aria-label={`Progress ${project.progress} percent`}
                      />
                      <span className="text-xs text-gray-500 mt-1">{project.progress}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {selectedProject && (
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50" role="dialog" aria-modal="true">
            <div className="bg-white rounded-lg shadow-xl max-w-lg w-full border">
              <div className="flex items-center justify-between px-6 py-4 border-b">
                <div>
                  <p className="text-sm text-gray-500">Project</p>
                  <h3 className="text-xl font-semibold text-gray-900">{selectedProject.name}</h3>
                </div>
                <button
                  onClick={() => setSelectedProject(null)}
                  className="text-gray-500 hover:text-gray-700 focus:outline-none"
                  aria-label="Close project details"
                >
                  ✕
                </button>
              </div>
              <div className="px-6 py-4 space-y-3">
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getRiskColor(selectedProject.risk)}`}>
                    {selectedProject.risk} Risk
                  </span>
                  <span className="text-sm text-gray-600">Budget: ${selectedProject.budget.toLocaleString()}</span>
                </div>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">Progress</p>
                  <progress
                    value={selectedProject.progress}
                    max={100}
                    className="w-full h-2 accent-blue-600 bg-gray-200 rounded-full overflow-hidden"
                    aria-label={`Progress ${selectedProject.progress} percent`}
                  />
                  <p className="text-sm text-gray-500">{selectedProject.progress}% complete</p>
                </div>
              </div>
              <div className="px-6 py-4 bg-gray-50 border-t flex justify-end">
                <button
                  onClick={() => setSelectedProject(null)}
                  className="px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* AI Insights */}
        <div className="bg-white rounded-lg shadow border">
          <div className="px-6 py-4 border-b">
            <h3 className="text-xl font-semibold">AI Risk Insights</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
                <div>
                  <p className="font-medium text-red-900">Critical Risk Detected</p>
                  <p className="text-red-700 text-sm">Data Migration project is 40% behind schedule with resource conflicts</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                <div>
                  <p className="font-medium text-yellow-900">Budget Risk Alert</p>
                  <p className="text-yellow-700 text-sm">E-commerce Platform may exceed budget by 15% based on current trends</p>
                </div>
              </div>
              
              <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <TrendingUp className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <p className="font-medium text-blue-900">Optimization Opportunity</p>
                  <p className="text-blue-700 text-sm">Reallocating 2 developers from Mobile App to Data Migration could reduce overall risk</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}