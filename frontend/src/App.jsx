import React, { useState, useEffect } from 'react';

const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [stats, setStats] = useState(null);
  const [insights, setInsights] = useState([]);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Interactive features state
  const [experimentRunning, setExperimentRunning] = useState(false);
  const [experimentProgress, setExperimentProgress] = useState(0);
  const [currentExperimentId, setCurrentExperimentId] = useState(null);
  const [numRuns, setNumRuns] = useState(10);
  const [analyzing, setAnalyzing] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [generatingInsights, setGeneratingInsights] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  // Poll experiment progress
  useEffect(() => {
    if (currentExperimentId && experimentRunning) {
      const pollInterval = setInterval(async () => {
        try {
          const res = await fetch(`${BACKEND_URL}/api/experiments/${currentExperimentId}`);
          const data = await res.json();
          
          setExperimentProgress(data.progress || 0);
          
          if (data.status === 'completed') {
            setExperimentRunning(false);
            setCurrentExperimentId(null);
            fetchData();
            // Auto-generate insights after experiment completes
            setTimeout(() => generateInsights(), 2000);
          } else if (data.status === 'failed') {
            setExperimentRunning(false);
            setCurrentExperimentId(null);
            alert('Experiment failed: ' + data.error);
          }
        } catch (error) {
          console.error('Error polling experiment:', error);
        }
      }, 2000);
      
      return () => clearInterval(pollInterval);
    }
  }, [currentExperimentId, experimentRunning]);

  const fetchData = async () => {
    try {
      const statsRes = await fetch(`${BACKEND_URL}/api/stats`);
      const statsData = await statsRes.json();
      setStats(statsData);

      const insightsRes = await fetch(`${BACKEND_URL}/api/insights`);
      const insightsData = await insightsRes.json();
      setInsights(insightsData || []);

      const runsRes = await fetch(`${BACKEND_URL}/api/runs`);
      const runsData = await runsRes.json();
      setRuns(Array.isArray(runsData) ? runsData.slice(-20) : []);

      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      setLoading(false);
    }
  };

  const runExperiment = async () => {
    try {
      setExperimentRunning(true);
      setExperimentProgress(0);
      
      const res = await fetch(`${BACKEND_URL}/api/experiments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ num_runs: numRuns })
      });
      
      const data = await res.json();
      setCurrentExperimentId(data.experiment_id);
    } catch (error) {
      console.error('Error starting experiment:', error);
      setExperimentRunning(false);
      alert('Failed to start experiment');
    }
  };

  const generateInsights = async () => {
    try {
      setGeneratingInsights(true);
      const res = await fetch(`${BACKEND_URL}/api/generate-insights`, {
        method: 'POST'
      });
      
      if (res.ok) {
        const data = await res.json();
        alert(`✅ AI Insights Generated!\n\n${data.cluster_name}\n${data.failure_count} failures analyzed`);
        fetchData(); // Refresh to show new insights
      } else {
        const error = await res.json();
        alert('Failed to generate insights: ' + error.detail);
      }
    } catch (error) {
      console.error('Error generating insights:', error);
      alert('Failed to generate insights');
    } finally {
      setGeneratingInsights(false);
    }
  };

  const analyzeRun = async (runId) => {
    try {
      setAnalyzing(runId);
      const res = await fetch(`${BACKEND_URL}/api/runs/${runId}/analysis`);
      const data = await res.json();
      setAnalysisResult({ runId, analysis: data });
    } catch (error) {
      console.error('Error analyzing run:', error);
      alert('Analysis failed');
    } finally {
      setAnalyzing(null);
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
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 shadow-lg">
        <h1 className="text-4xl font-bold">⚡ FailSim AI</h1>
        <p className="text-gray-200 mt-2">
          Interactive Failure Discovery & Root-Cause Analysis for Robotics
        </p>
        <p className="text-sm text-gray-300 mt-1">
          🤖 Kuka iiwa7 Robot | 🔬 Physics-Based Simulation | 🧠 Gemini 3 Flash AI
        </p>
      </header>

      <main className="container mx-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard title="Total Simulations" value={stats?.total_runs || 0} color="bg-blue-600" />
          <StatCard title="Successes" value={stats?.successes || 0} color="bg-green-600" />
          <StatCard title="Failures" value={stats?.failures || 0} color="bg-red-600" />
          <StatCard title="Success Rate" value={`${stats?.success_rate || 0}%`} color="bg-purple-600" />
        </div>

        <div className="bg-gradient-to-r from-purple-800 to-blue-800 rounded-lg p-6 mb-8 shadow-xl">
          <h2 className="text-2xl font-bold mb-4">🎮 Interactive Control Panel</h2>
          <div className="flex items-center gap-4 flex-wrap">
            <div>
              <label className="block text-sm mb-2">Number of Runs:</label>
              <input
                type="number"
                value={numRuns}
                onChange={(e) => setNumRuns(Number(e.target.value))}
                min="1"
                max="50"
                className="bg-gray-700 text-white px-4 py-2 rounded-lg w-24"
                disabled={experimentRunning}
              />
            </div>
            <div className="flex-1">
              <button
                onClick={runExperiment}
                disabled={experimentRunning}
                className={`${
                  experimentRunning ? 'bg-gray-600 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
                } text-white px-6 py-2 rounded-lg font-semibold transition mt-6`}
              >
                {experimentRunning ? '🔄 Running...' : '▶️ Run New Experiment'}
              </button>
            </div>
            <div>
              <button
                onClick={generateInsights}
                disabled={generatingInsights || (stats?.failures || 0) < 3}
                className={`${
                  generatingInsights || (stats?.failures || 0) < 3
                    ? 'bg-gray-600 cursor-not-allowed'
                    : 'bg-yellow-600 hover:bg-yellow-700'
                } text-white px-6 py-2 rounded-lg font-semibold transition mt-6`}
                title={(stats?.failures || 0) < 3 ? 'Need at least 3 failures' : 'Generate AI insights from failures'}
              >
                {generatingInsights ? '🧠 Analyzing...' : '🧠 Generate AI Insights'}
              </button>
            </div>
          </div>

          {experimentRunning && (
            <div className="mt-4">
              <div className="flex justify-between text-sm mb-2">
                <span>Progress: {experimentProgress}%</span>
                <span>Experiment ID: {currentExperimentId}</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-4">
                <div
                  className="bg-green-500 h-4 rounded-full transition-all duration-500"
                  style={{ width: `${experimentProgress}%` }}
                />
              </div>
            </div>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg p-6 mb-8 shadow-xl">
          <h2 className="text-3xl font-bold mb-4 flex items-center">
            <span className="mr-3">🧠</span> Gemini AI Analysis
          </h2>

          {insights.length === 0 ? (
            <div className="text-gray-400 text-center py-8">
              No AI insights yet. Run experiments then click "Generate AI Insights" button above.
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
                      {insight.failure_count} failures ({insight.percentage?.toFixed(0)}%)
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
                  <th className="p-3 text-left">Action</th>
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
                    <td className="p-3">
                      <button
                        onClick={() => analyzeRun(run.run_id)}
                        disabled={analyzing === run.run_id}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-3 py-1 rounded text-xs"
                      >
                        {analyzing === run.run_id ? '⏳' : '🔍 Analyze'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {analysisResult && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-2xl font-bold text-blue-400">
                  🧠 AI Analysis: {analysisResult.runId}
                </h3>
                <button
                  onClick={() => setAnalysisResult(null)}
                  className="text-gray-400 hover:text-white text-2xl"
                >
                  ×
                </button>
              </div>
              
              <div className="bg-gray-700 rounded-lg p-4 mb-4">
                <p className="text-sm text-gray-400 mb-2">
                  Outcome: <span className={analysisResult.analysis.outcome === 'success' ? 'text-green-400' : 'text-red-400'}>
                    {analysisResult.analysis.outcome?.toUpperCase()}
                  </span>
                </p>
              </div>

              <div className="bg-gradient-to-r from-yellow-900 to-orange-900 rounded-lg p-4">
                <h4 className="font-semibold text-yellow-300 mb-3">Gemini 3 Flash Analysis:</h4>
                <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">
                  {analysisResult.analysis.root_cause}
                </p>
              </div>

              <button
                onClick={() => setAnalysisResult(null)}
                className="mt-4 bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg w-full"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </main>

      <footer className="bg-gray-800 text-center p-4 mt-8 text-gray-400">
        <p>FailSim AI • Built for Launch & Fund Hackathon • Track 2: Simulation-to-Real</p>
        <p className="text-sm mt-1">Backend: Vultr • AI: Gemini 3 Flash • Physics: PyBullet</p>
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
