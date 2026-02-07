import React, { useState, useEffect } from 'react';
import './App.css';

const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [stats, setStats] = useState(null);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    // Refresh every 5 seconds
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      // Fetch statistics
      const statsRes = await fetch(`${BACKEND_URL}/api/stats`);
      const statsData = await statsRes.json();
      setStats(statsData);

      // Fetch AI insights
      const insightsRes = await fetch(`${BACKEND_URL}/api/insights`);
      const insightsData = await insightsRes.json();
      setInsights(insightsData.insights || []);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading FailSim AI...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-6">
        <h1 className="text-3xl font-bold">FailSim AI Dashboard</h1>
        <p className="text-gray-400 mt-2">
          Automatic failure discovery & root-cause analysis for robotics
        </p>
      </header>

      {/* Main Content */}
      <main className="container mx-auto p-6">
        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Runs"
            value={stats?.total_runs || 0}
            color="blue"
          />
          <StatCard
            title="Successes"
            value={stats?.successes || 0}
            color="green"
          />
          <StatCard
            title="Failures"
            value={stats?.failures || 0}
            color="red"
          />
          <StatCard
            title="Success Rate"
            value={`${stats?.success_rate || 0}%`}
            color="purple"
          />
        </div>

        {/* AI Insights */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-2xl font-bold mb-4">🧠 Gemini Pro Analysis</h2>

          {insights.length === 0 ? (
            <div className="text-gray-400 text-center py-8">
              No AI insights yet. Run simulations and analysis to see results.
            </div>
          ) : (
            <div className="space-y-6">
              {insights.map((insight, idx) => (
                <div key={idx} className="bg-gray-700 rounded-lg p-6">
                  <h3 className="text-xl font-semibold mb-2">
                    {insight.cluster_name}
                  </h3>
                  <p className="text-gray-400 mb-4">
                    {insight.failure_count} failures ({insight.percentage}%)
                  </p>

                  <div className="mb-4">
                    <h4 className="font-semibold text-yellow-400 mb-2">
                      Root Cause:
                    </h4>
                    <p className="text-gray-300">{insight.root_cause}</p>
                  </div>

                  <div>
                    <h4 className="font-semibold text-red-400 mb-2">
                      Failure Mechanism:
                    </h4>
                    <p className="text-gray-300">{insight.failure_mechanism}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function StatCard({ title, value, color }) {
  const colors = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    red: 'bg-red-600',
    purple: 'bg-purple-600',
  };

  return (
    <div className={`${colors[color]} rounded-lg p-6`}>
      <h3 className="text-sm font-semibold opacity-80 mb-2">{title}</h3>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  );
}

export default App;
