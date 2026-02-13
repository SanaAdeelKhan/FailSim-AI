import React, { useState, useEffect } from 'react';

const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [stats, setStats] = useState(null);
  const [insights, setInsights] = useState([]);
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [robots, setRobots] = useState({});
  const [selectedRobot, setSelectedRobot] = useState('kuka_iiwa7');
  const [analytics, setAnalytics] = useState(null);
  
  // Interactive features
  const [experimentRunning, setExperimentRunning] = useState(false);
  const [experimentProgress, setExperimentProgress] = useState(0);
  const [currentExperimentId, setCurrentExperimentId] = useState(null);
  const [numRuns, setNumRuns] = useState(10);
  const [analyzing, setAnalyzing] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [generatingInsights, setGeneratingInsights] = useState(false);
  
  // Visualization
  const [simulationFrames, setSimulationFrames] = useState(null);
  const [capturingFrames, setCapturingFrames] = useState(false);
  const [showVisualization, setShowVisualization] = useState(false);
  
  // Custom robot
  const [showCustomRobotForm, setShowCustomRobotForm] = useState(false);
  const [customRobot, setCustomRobot] = useState({
    name: '',
    description: '',
    max_payload: 5.0,
    max_gripper_force: 100,
    max_acceleration: 5.0,
    dof: 6,
    reach: 800,
    use_case: ''
  });

  useEffect(() => {
    fetchData();
    fetchRobots();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

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
      const [statsRes, insightsRes, runsRes, analyticsRes] = await Promise.all([
        fetch(`${BACKEND_URL}/api/stats`),
        fetch(`${BACKEND_URL}/api/insights`),
        fetch(`${BACKEND_URL}/api/runs`),
        fetch(`${BACKEND_URL}/api/analytics/failure-distribution`)
      ]);

      const statsData = await statsRes.json();
      const insightsData = await insightsRes.json();
      const runsData = await runsRes.json();
      const analyticsData = await analyticsRes.json();

      setStats(statsData);
      setInsights(insightsData || []);
      setRuns(Array.isArray(runsData) ? runsData.slice(-20) : []);
      setAnalytics(analyticsData);
      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
      setLoading(false);
    }
  };

  const fetchRobots = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/robots`);
      const data = await res.json();
      setRobots(data.robots || {});
    } catch (error) {
      console.error('Error fetching robots:', error);
    }
  };

  const createCustomRobot = async () => {
    if (!customRobot.name) {
      alert('Please enter a robot name');
      return;
    }
    
    try {
      const res = await fetch(`${BACKEND_URL}/api/robots/custom`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(customRobot)
      });
      
      const data = await res.json();
      
      // Add to robots list
      setRobots(prev => ({
        ...prev,
        [data.robot_id]: data.config
      }));
      
      // Select the new robot
      setSelectedRobot(data.robot_id);
      
      // Close form
      setShowCustomRobotForm(false);
      
      // Reset form
      setCustomRobot({
        name: '',
        description: '',
        max_payload: 5.0,
        max_gripper_force: 100,
        max_acceleration: 5.0,
        dof: 6,
        reach: 800,
        use_case: ''
      });
      
      alert(`✅ Custom robot "${data.config.name}" created!`);
    } catch (error) {
      console.error('Error creating custom robot:', error);
      alert('Failed to create custom robot');
    }
  };

  const runExperiment = async () => {
    try {
      setExperimentRunning(true);
      setExperimentProgress(0);
      
      const res = await fetch(`${BACKEND_URL}/api/experiments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          num_runs: numRuns,
          robot_type: selectedRobot
        })
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
        fetchData();
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

  const captureSimulation = async () => {
    try {
      setCapturingFrames(true);
      const res = await fetch(`${BACKEND_URL}/api/simulate-with-frames`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          weight: 0.8,
          friction: 0.5,
          lighting: 0.5,
          robot_type: selectedRobot
        })
      });
      
      const data = await res.json();
      setSimulationFrames(data.frames);
      setShowVisualization(true);
    } catch (error) {
      console.error('Error capturing frames:', error);
      alert('Failed to capture simulation frames');
    } finally {
      setCapturingFrames(false);
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

  const currentRobot = robots[selectedRobot] || {};

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 shadow-lg">
        <h1 className="text-4xl font-bold">⚡ FailSim AI</h1>
        <p className="text-gray-200 mt-2">
          Multi-Robot Failure Discovery & Root-Cause Analysis Platform
        </p>
        <p className="text-sm text-gray-300 mt-1">
          🤖 Physics-Based Simulation | 🧠 Gemini 3 Flash AI | 📊 Real-time Analytics
        </p>
      </header>

      <main className="container mx-auto p-6">
        {/* Stats Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard title="Total Simulations" value={stats?.total_runs || 0} color="bg-blue-600" />
          <StatCard title="Successes" value={stats?.successes || 0} color="bg-green-600" />
          <StatCard title="Failures" value={stats?.failures || 0} color="bg-red-600" />
          <StatCard title="Success Rate" value={`${stats?.success_rate || 0}%`} color="bg-purple-600" />
        </div>

        {/* Robot Selection */}
        <div className="bg-gradient-to-r from-indigo-800 to-purple-800 rounded-lg p-6 mb-8 shadow-xl">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">🤖 Robot Configuration</h2>
            <button
              onClick={() => setShowCustomRobotForm(true)}
              className="bg-yellow-600 hover:bg-yellow-700 px-4 py-2 rounded-lg font-semibold"
            >
              + Add Custom Robot
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {Object.entries(robots).map(([id, robot]) => (
              <div
                key={id}
                onClick={() => setSelectedRobot(id)}
                className={`cursor-pointer p-4 rounded-lg border-2 transition ${
                  selectedRobot === id
                    ? 'border-yellow-400 bg-gray-700'
                    : 'border-gray-600 bg-gray-800 hover:border-gray-500'
                }`}
              >
                <h3 className="text-xl font-bold mb-2">{robot.name}</h3>
                <p className="text-sm text-gray-300 mb-3">{robot.description}</p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-400">Payload:</span>
                    <span className="ml-1 font-semibold">{robot.max_payload}kg</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Force:</span>
                    <span className="ml-1 font-semibold">{robot.max_gripper_force}N</span>
                  </div>
                  <div>
                    <span className="text-gray-400">DOF:</span>
                    <span className="ml-1 font-semibold">{robot.dof}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Reach:</span>
                    <span className="ml-1 font-semibold">{robot.reach}mm</span>
                  </div>
                </div>
                <p className="text-xs text-blue-300 mt-2">📍 {robot.use_case}</p>
              </div>
            ))}
          </div>

          <div className="bg-gray-700 rounded-lg p-4">
            <h3 className="font-bold mb-2">Selected: {currentRobot.name}</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-400">Max Payload:</span>
                <p className="font-semibold text-lg">{currentRobot.max_payload} kg</p>
              </div>
              <div>
                <span className="text-gray-400">Gripper Force:</span>
                <p className="font-semibold text-lg">{currentRobot.max_gripper_force} N</p>
              </div>
              <div>
                <span className="text-gray-400">Acceleration:</span>
                <p className="font-semibold text-lg">{currentRobot.max_acceleration} m/s²</p>
              </div>
              <div>
                <span className="text-gray-400">Reach:</span>
                <p className="font-semibold text-lg">{currentRobot.reach} mm</p>
              </div>
            </div>
          </div>
        </div>

        {/* Control Panel */}
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
                {experimentRunning ? '🔄 Running...' : '▶️ Run Experiment'}
              </button>
            </div>
            <div>
              <button
                onClick={captureSimulation}
                disabled={capturingFrames}
                className={`${
                  capturingFrames ? 'bg-gray-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                } text-white px-6 py-2 rounded-lg font-semibold transition mt-6`}
              >
                {capturingFrames ? '📸 Capturing...' : '📸 Visualize Simulation'}
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
                title={(stats?.failures || 0) < 3 ? 'Need at least 3 failures' : 'Generate AI insights'}
              >
                {generatingInsights ? '🧠 Analyzing...' : '🧠 Generate Insights'}
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

        {/* Analytics Charts */}
        {analytics && (stats?.failures || 0) > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <ChartCard title="Error Types Distribution" data={analytics.error_types} />
            <ChartCard title="Weight Distribution (Failures)" data={analytics.weight_distribution} type="weight" />
          </div>
        )}

        {/* AI Insights */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8 shadow-xl">
          <h2 className="text-3xl font-bold mb-4 flex items-center">
            <span className="mr-3">🧠</span> Gemini AI Analysis
          </h2>

          {insights.length === 0 ? (
            <div className="text-gray-400 text-center py-8">
              No AI insights yet. Run experiments then click "Generate Insights" button above.
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

        {/* Recent Runs */}
        <div className="bg-gray-800 rounded-lg p-6 shadow-xl">
          <h2 className="text-2xl font-bold mb-4">📊 Recent Simulation Runs</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-700">
                <tr>
                  <th className="p-3 text-left">Run ID</th>
                  <th className="p-3 text-left">Robot</th>
                  <th className="p-3 text-left">Status</th>
                  <th className="p-3 text-left">Weight</th>
                  <th className="p-3 text-left">Friction</th>
                  <th className="p-3 text-left">Error</th>
                  <th className="p-3 text-left">Action</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run, idx) => (
                  <tr key={idx} className="border-b border-gray-700 hover:bg-gray-700">
                    <td className="p-3 font-mono text-xs">{run.run_id}</td>
                    <td className="p-3 text-xs">{robots[run.robot_type]?.name || run.robot_type}</td>
                    <td className="p-3">
                      {run.success ? (
                        <span className="text-green-400">✅ SUCCESS</span>
                      ) : (
                        <span className="text-red-400">❌ FAILED</span>
                      )}
                    </td>
                    <td className="p-3">{run.object_weight?.toFixed(2)}kg</td>
                    <td className="p-3">{run.surface_friction?.toFixed(2)}</td>
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

        {/* Custom Robot Form Modal */}
        {showCustomRobotForm && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full">
              <h3 className="text-2xl font-bold mb-4">🤖 Create Custom Robot</h3>
              
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="Robot Name"
                  value={customRobot.name}
                  onChange={(e) => setCustomRobot({...customRobot, name: e.target.value})}
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded"
                />
                <input
                  type="text"
                  placeholder="Description"
                  value={customRobot.description}
                  onChange={(e) => setCustomRobot({...customRobot, description: e.target.value})}
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded"
                />
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs text-gray-400">Max Payload (kg)</label>
                    <input
                      type="number"
                      value={customRobot.max_payload}
                      onChange={(e) => setCustomRobot({...customRobot, max_payload: Number(e.target.value)})}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400">Gripper Force (N)</label>
                    <input
                      type="number"
                      value={customRobot.max_gripper_force}
                      onChange={(e) => setCustomRobot({...customRobot, max_gripper_force: Number(e.target.value)})}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400">Max Accel (m/s²)</label>
                    <input
                      type="number"
                      value={customRobot.max_acceleration}
                      onChange={(e) => setCustomRobot({...customRobot, max_acceleration: Number(e.target.value)})}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400">DOF</label>
                    <input
                      type="number"
                      value={customRobot.dof}
                      onChange={(e) => setCustomRobot({...customRobot, dof: Number(e.target.value)})}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Reach (mm)</label>
                  <input
                    type="number"
                    value={customRobot.reach}
                    onChange={(e) => setCustomRobot({...customRobot, reach: Number(e.target.value)})}
                    className="w-full bg-gray-700 text-white px-3 py-2 rounded"
                  />
                </div>
                <input
                  type="text"
                  placeholder="Use Case"
                  value={customRobot.use_case}
                  onChange={(e) => setCustomRobot({...customRobot, use_case: e.target.value})}
                  className="w-full bg-gray-700 text-white px-3 py-2 rounded"
                />
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={createCustomRobot}
                  className="flex-1 bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg"
                >
                  Create Robot
                </button>
                <button
                  onClick={() => setShowCustomRobotForm(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Analysis Modal */}
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
                {analysisResult.analysis.model_used && (
                  <p className="text-xs text-gray-500">Model: {analysisResult.analysis.model_used}</p>
                )}
              </div>

              <div className="bg-gradient-to-r from-yellow-900 to-orange-900 rounded-lg p-4">
                <h4 className="font-semibold text-yellow-300 mb-3">Gemini AI Analysis:</h4>
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

        {/* Simulation Frames Modal */}
        {showVisualization && simulationFrames && (
          <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-2xl font-bold text-purple-400">
                  📸 Simulation Visualization - {currentRobot.name}
                </h3>
                <button
                  onClick={() => setShowVisualization(false)}
                  className="text-gray-400 hover:text-white text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {simulationFrames.map((frame, idx) => (
                  <div key={idx} className="bg-gray-700 rounded-lg p-3">
                    <h4 className="font-semibold text-yellow-300 mb-2">{frame.label}</h4>
                    <img 
                      src={frame.image} 
                      alt={frame.label}
                      className="w-full rounded border border-gray-600"
                    />
                    <p className="text-xs text-gray-400 mt-2">Step: {frame.step}/240</p>
                  </div>
                ))}
              </div>

              <button
                onClick={() => setShowVisualization(false)}
                className="mt-4 bg-purple-600 hover:bg-purple-700 px-6 py-2 rounded-lg w-full"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </main>

      <footer className="bg-gray-800 text-center p-4 mt-8 text-gray-400">
        <p>FailSim AI • Multi-Robot Failure Analysis Platform</p>
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

function ChartCard({ title, data, type = 'error' }) {
  if (!data) return null;
  
  const chartData = type === 'error' 
    ? Object.entries(data).map(([key, value]) => ({ label: key, value }))
    : data;
  
  const maxValue = Math.max(...chartData.map(d => d.count || d.value || 0), 1);
  
  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-xl font-bold mb-4">{title}</h3>
      <div className="space-y-3">
        {chartData.map((item, idx) => {
          const value = item.count || item.value || 0;
          const percentage = (value / maxValue) * 100;
          const label = item.range || item.label;
          
          return (
            <div key={idx}>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-300">{label}</span>
                <span className="font-semibold">{value}</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-3">
                <div
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all"
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default App;
