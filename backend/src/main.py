"""
FailSim AI - Backend API
Runs on Vultr VM - central system of record
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime
import os

app = FastAPI(title="FailSim AI Backend")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database later)
simulation_runs = []
ai_insights = []

# ============================================
# DATA MODELS
# ============================================

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

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/")
def read_root():
    return {
        "service": "FailSim AI Backend",
        "status": "running",
        "version": "0.1.0",
        "vultr": "enabled"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "total_runs": len(simulation_runs),
        "total_insights": len(ai_insights)
    }

@app.post("/api/runs")
def submit_run(run: SimulationRun):
    """Store simulation run from Wajiha's simulation"""
    simulation_runs.append(run.dict())
    return {
        "status": "success",
        "run_id": run.run_id,
        "total_runs": len(simulation_runs)
    }

@app.post("/api/runs/batch")
def submit_batch(runs: List[SimulationRun]):
    """Store multiple runs at once"""
    for run in runs:
        simulation_runs.append(run.dict())
    return {
        "status": "success",
        "runs_added": len(runs),
        "total_runs": len(simulation_runs)
    }

@app.get("/api/runs")
def get_all_runs():
    """Get all simulation runs"""
    return {
        "total": len(simulation_runs),
        "runs": simulation_runs
    }

@app.get("/api/runs/failures")
def get_failures():
    """Get only failed runs for AI analysis"""
    failures = [run for run in simulation_runs if not run["success"]]
    return {
        "total_failures": len(failures),
        "failures": failures
    }

@app.get("/api/stats")
def get_statistics():
    """Get success/failure statistics for dashboard"""
    if not simulation_runs:
        return {
            "total_runs": 0,
            "success_rate": 0,
            "failure_rate": 0
        }
    
    total = len(simulation_runs)
    successes = sum(1 for run in simulation_runs if run["success"])
    
    return {
        "total_runs": total,
        "successes": successes,
        "failures": total - successes,
        "success_rate": round((successes / total) * 100, 2),
        "failure_rate": round(((total - successes) / total) * 100, 2)
    }

@app.post("/api/insights")
def submit_insight(insight: AIInsight):
    """Store AI-generated insight from Gemini"""
    ai_insights.append(insight.dict())
    return {
        "status": "success",
        "total_insights": len(ai_insights)
    }

@app.get("/api/insights")
def get_insights():
    """Get all AI insights for dashboard"""
    return {
        "total": len(ai_insights),
        "insights": ai_insights
    }

# ============================================
# RUN SERVER
# ============================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
