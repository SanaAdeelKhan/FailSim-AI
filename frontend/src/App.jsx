import React, { useState, useEffect } from 'react';

const BACKEND_URL = 'http://80.240.20.49:8000';

function App() {
  const [stats, setStats] = useState(null);
  const [insights, setInsights] = useState([]);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // Fetch stats
      const statsRes = await fetch(`${BACKEND_URL}/api/stats`);
      const statsData = await statsRes.json();
      setStats(statsData);

      // Fetch insights
      const insightsRes = await fetch(`${BACKEND_URL}/api/insights`);
      const insightsData = await insightsRes.json();
      setInsights(insightsData.insights || []);

      // Fetch recent runs
      const runsRes = await fetch(`${BACKEND_URL}/api/runs`);
      const runsData = await runsRes.json();
      setRuns(runsData.runs?.slice(-20) || []); // Last 20 runs

      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading FailSim AI Dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 shadow-lg">
        <h1 className="text-4xl font-bold">⚡ FailSim AI</h1>
        <p className="text-gray-200 mt-2">
          Automatic Failure Discovery & Root-Cause Analysis for Robotics
        </p>
        <p className="text-sm text-gray-300 mt-1">
          🤖 Kuka iiwa7 Robot | 🔬 Physics-Based Simulation | 🧠 Gemini 2.5 Flash AI
        </p>
      </header>

      {/* Stats Dashboard */}
      <main className="container mx-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard title="Total Simulations" value={stats?.total_runs || 0} color="bg-blue-600" />
          <StatCard title="Successes" value={stats?.successes || 0} color="bg-green-600" />
          <StatCard title="Failures" value={stats?.failures || 0} color="bg-red-600" />
          <StatCard 
            title="Success Rate" 
            value={`${stats?.success_rate || 0}%`} 
            color="bg-purple-600" 
          />
        </div>

        {/* Gemini AI Insights */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8 shadow-xl">
          <h2 className="text-3xl font-bold mb-4 flex items-center">
            <span className="mr-3">🧠</span> Gemini AI Analysis
          </h2>

          {insights.length === 0 ? (
            <div className="text-gray-400 text-center py-8">
              No AI insights yet. Run simulations and analysis to see results.
            </div>
          ) : (
            <div className="space-y-6">
              {insights.slice(-3).reverse().map((insight, idx) => (
                <div key={idx} className="bg-gradient-to-r from-gray-700 to-gray-800 rounded-lg p-6 border-l-4 border-yellow-500">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-2xl font-semibold text-yellow-400">
                      {insight.cluster_name}
                    </h3>
                    <span className="bg-red-600 px-3 py-1 rounded-full text-sm">
                      {insight.failure_count} failures ({insight.percentage.toFixed(0)}%)
                    </span>
                  </div>

                  <div className="mb-4">
                    <h4 className="font-semibold text-yellow-300 mb-2 text-lg">
                      💡 Root Cause:
                    </h4>
                    <p className="text-gray-200 leading-relaxed">{insight.root_cause}</p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-red-300 mb-2 text-lg">
                      ⚙️ Failure Mechanism:
                    </h4>
                    <p className="text-gray-200 leading-relaxed">{insight.failure_mechanism}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Runs */}
        <div className="bg-gray-800 rounded-lg p-6 shadow-xl">
          <h2 className="text-2xl font-bold mb-4">📊 Recent Simulation Runs</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-700">
                <tr>
                  <th className="p-3 text-left">Run ID</th>
                  <th className="p-3 text-left">Status</th>
                  <th className="p-3 text-left">Weight (kg)</th>
                  <th className="p-3 text-left">Friction</th>
                  <th className="p-3 text-left">Lighting</th>
                  <th className="p-3 text-left">Error Type</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run, idx) => (
                  <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700">
                    <td className="p-3 font-mono text-xs">{run.run_id}</td>
                    <td className="p-3">
                      {run.success ? (
                        <span className="text-green-400">✅ SUCCESS</span>
                      ) : (
                        <span className="text-red-400">❌ FAILED</span>
                      )}
                    </td>
                    <td className="p-3">{run.object_weight?.toFixed(2)}</td>
                    <td className="p-3">{run.surface_friction?.toFixed(2)}</td>
                    <td className="p-3">{run.lighting_variance?.toFixed(2)}</td>
                    <td className="p-3 text-gray-400">{run.error_type || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-center p-4 mt-8 text-gray-400">
        <p>FailSim AI • Built for Launch & Fund Hackathon • Track 2: Simulation-to-Real</p>
        <p className="text-sm mt-1">Backend: Vultr • AI: Gemini 2.5 Flash • Physics: PyBullet</p>
      </footer>
    </div>
  );
}

function StatCard({ title, value, color }) {
  return (
    <div className={`${color} rounded-lg p-6 shadow-lg`}>
      <h3 className="text-sm font-semibold opacity-80 mb-2">{title}</h3>
      <p className="text-4xl font-bold">{value}</p>
    </div>
  );
}

export default App;
