"""
FailSim AI - Backend API with Debug Logging
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime
import os
import sys
from pathlib import Path
import uuid
from threading import Thread
import traceback  # ADD THIS

# Add simulation directory to path
backend_dir = Path(__file__).parent.parent
project_root = backend_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "simulation"))

app = FastAPI(title="FailSim AI Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage
simulation_runs = []
ai_insights = []
experiments = {}

# DATA MODELS
class SimulationRun(BaseModel):
    run_id: str
    success: bool
    time_seconds: float
    object_weight: float
    surface_friction: float
    lighting_variance: float
    distance_from_target: float
    dropped: bool
    error_type: Optional[str] = None
    timestamp: str = datetime.now().isoformat()

class AIInsight(BaseModel):
    cluster_name: str
    failure_count: int
    total_runs: int
    percentage: float
    root_cause: str
    failure_mechanism: str
    timestamp: str = datetime.now().isoformat()

class ExperimentRequest(BaseModel):
    num_runs: int = 10
    object_weight: Optional[float] = None
    surface_friction: Optional[float] = None
    lighting_variance: Optional[float] = None

# ENDPOINTS
@app.get("/")
def read_root():
    return {"service": "FailSim AI Backend", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "total_runs": len(simulation_runs)}

@app.post("/api/runs")
def submit_run(run: SimulationRun):
    simulation_runs.append(run.model_dump())
    return {"status": "success", "run_id": run.run_id}

@app.post("/api/runs/batch")
def submit_batch(runs: List[SimulationRun]):
    for run in runs:
        simulation_runs.append(run.model_dump())
    return {"status": "success", "runs_added": len(runs)}

@app.get("/api/runs")
def get_all_runs():
    return simulation_runs

@app.get("/api/stats")
def get_statistics():
    if not simulation_runs:
        return {"total_runs": 0, "success_rate": 0, "failure_rate": 0}
    total = len(simulation_runs)
    successes = sum(1 for run in simulation_runs if run["success"])
    return {
        "total_runs": total,
        "successes": successes,
        "failures": total - successes,
        "success_rate": round((successes / total) * 100, 2),
        "failure_rate": round(((total - successes) / total) * 100, 2)
    }

@app.get("/api/insights")
def get_insights():
    return ai_insights

@app.post("/api/insights")
def submit_insight(insight: AIInsight):
    """Store AI-generated insight from Gemini"""
    ai_insights.append(insight.model_dump())
    return {
        "status": "success",
        "total_insights": len(ai_insights)
    }

@app.post("/api/generate-insights")
def generate_insights():
    """Generate AI insights from current failures"""
    try:
        failures = [r for r in simulation_runs if not r['success']]
        
        if len(failures) < 3:
            raise HTTPException(status_code=400, detail="Need at least 3 failures to analyze")
        
        # Import and run analyzer
        from ai.analysis.gemini_analyzer import analyze_failure_cluster
        
        result = analyze_failure_cluster(failures)
        
        if result:
            insight_data = {
                "cluster_name": result["cluster_name"],
                "failure_count": result["failure_count"],
                "total_runs": len(simulation_runs),
                "percentage": float((result["failure_count"] / len(simulation_runs)) * 100),
                "root_cause": result["root_cause"],
                "failure_mechanism": result["failure_mechanism"],
                "timestamp": datetime.now().isoformat()
            }
            
            ai_insights.append(insight_data)
            return insight_data
        else:
            raise HTTPException(status_code=500, detail="Analysis failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# INTERACTIVE FEATURES
@app.post("/api/experiments")
def create_experiment(request: ExperimentRequest):
    experiment_id = f"EXP_{uuid.uuid4().hex[:8]}"
    
    experiments[experiment_id] = {
        "id": experiment_id,
        "status": "running",
        "progress": 0,
        "total_runs": request.num_runs,
        "completed_runs": 0,
        "params": request.model_dump(),
        "results": [],
        "started_at": datetime.now().isoformat()
    }
    
    def run_simulation_async():
        try:
            print(f"\n🚀 Starting experiment {experiment_id}")
            print(f"Attempting to import PickPlaceRobot...")
            
            from robot_pick_place import PickPlaceRobot
            import random
            
            print("✅ Import successful!")
            print(f"Creating robot simulator...")
            
            robot = PickPlaceRobot(gui=False)
            print("✅ Robot created!")
            
            results = []
            
            for i in range(request.num_runs):
                weight = request.object_weight if request.object_weight else random.uniform(0.3, 1.5)
                friction = request.surface_friction if request.surface_friction else random.uniform(0.1, 0.8)
                lighting = request.lighting_variance if request.lighting_variance else random.uniform(0.3, 1.0)
                
                run_id = f"EXP_{experiment_id[-8:]}_{i:03d}"
                
                print(f"Running simulation {i+1}/{request.num_runs}...")
                
                success, time_sec, dist_error, error_type, dropped = robot.simulate_pick_place(
                    weight, friction, lighting
                )
                
                run_data = {
                    "run_id": run_id,
                    "success": success,
                    "time_seconds": round(time_sec, 2),
                    "object_weight": round(weight, 2),
                    "surface_friction": round(friction, 2),
                    "lighting_variance": round(lighting, 2),
                    "distance_from_target": round(dist_error, 3),
                    "dropped": dropped,
                    "error_type": error_type,
                    "timestamp": datetime.now().isoformat()
                }
                
                results.append(run_data)
                simulation_runs.append(run_data)
                
                experiments[experiment_id]["completed_runs"] += 1
                experiments[experiment_id]["progress"] = int(
                    (experiments[experiment_id]["completed_runs"] / request.num_runs) * 100
                )
                
                print(f"✅ Run {i+1} complete: {'SUCCESS' if success else 'FAILURE'}")
            
            robot.close()
            
            experiments[experiment_id]["status"] = "completed"
            experiments[experiment_id]["results"] = results
            experiments[experiment_id]["completed_at"] = datetime.now().isoformat()
            
            print(f"✅ Experiment {experiment_id} completed successfully!")
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"\n❌ EXPERIMENT FAILED: {error_msg}")
            print(f"Traceback:\n{traceback.format_exc()}")
            
            experiments[experiment_id]["status"] = "failed"
            experiments[experiment_id]["error"] = error_msg
            experiments[experiment_id]["traceback"] = traceback.format_exc()
    
    thread = Thread(target=run_simulation_async, daemon=True)
    thread.start()
    
    return {
        "experiment_id": experiment_id,
        "status": "running",
        "message": f"Experiment started with {request.num_runs} runs"
    }

@app.get("/api/experiments/{experiment_id}")
def get_experiment_status(experiment_id: str):
    if experiment_id not in experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiments[experiment_id]

@app.get("/api/runs/{run_id}/analysis")
def analyze_run(run_id: str):
    run = next((r for r in simulation_runs if r["run_id"] == run_id), None)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-3-flash-preview")
        
        prompt = f"""Analyze this robotic simulation run briefly (3-4 sentences):
Run: {run['run_id']} - {'SUCCESS' if run['success'] else 'FAILURE'}
Weight: {run['object_weight']}kg, Friction: {run['surface_friction']}, Lighting: {run['lighting_variance']}
Error: {run.get('error_type', 'N/A')}

Explain the root cause and give one specific recommendation."""

        response = model.generate_content(prompt)
        
        return {
            "run_id": run_id,
            "outcome": "success" if run['success'] else "failure",
            "root_cause": response.text,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
