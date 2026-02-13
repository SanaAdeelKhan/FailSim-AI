"""
FailSim AI - Backend API with Multi-Robot Support
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
from datetime import datetime
import os
import sys
from pathlib import Path
import uuid
from threading import Thread
import traceback

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

# Robot Configurations
robot_configs = {
    "kuka_iiwa7": {
        "name": "Kuka iiwa7",
        "description": "Industrial 7-DOF collaborative robot",
        "max_payload": 7.0,
        "max_gripper_force": 100,
        "max_acceleration": 5.0,
        "dof": 7,
        "reach": 800,
        "use_case": "Precision assembly, medical robotics",
        "urdf": "kuka_iiwa/model.urdf"
    },
    "franka_panda": {
        "name": "Franka Emika Panda",
        "description": "Research-grade collaborative robot",
        "max_payload": 3.0,
        "max_gripper_force": 70,
        "max_acceleration": 13.0,
        "dof": 7,
        "reach": 855,
        "use_case": "Research, human-robot collaboration",
        "urdf": "franka_panda/panda.urdf"
    },
    "ur5": {
        "name": "Universal Robots UR5",
        "description": "Versatile collaborative robot",
        "max_payload": 5.0,
        "max_gripper_force": 150,
        "max_acceleration": 3.0,
        "dof": 6,
        "reach": 850,
        "use_case": "Manufacturing, pick-and-place",
        "urdf": "ur5/ur5.urdf"
    }
}

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
    robot_type: Optional[str] = "kuka_iiwa7"
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
    robot_type: Optional[str] = "kuka_iiwa7"

# BASIC ENDPOINTS
@app.get("/")
def read_root():
    return {"service": "FailSim AI Backend", "status": "running", "version": "2.0"}

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
    return {"status": "success", "total_insights": len(ai_insights)}

# ROBOT CONFIGURATION ENDPOINTS
@app.get("/api/robots")
def get_robot_configs():
    """Get available robot configurations"""
    return {"robots": robot_configs}

@app.get("/api/robots/{robot_id}")
def get_robot_config(robot_id: str):
    """Get specific robot configuration"""
    if robot_id not in robot_configs:
        raise HTTPException(status_code=404, detail="Robot not found")
    return robot_configs[robot_id]

# ANALYTICS ENDPOINTS
@app.get("/api/analytics/failure-distribution")
def get_failure_distribution():
    """Get failure distribution for visualization"""
    if not simulation_runs:
        return {
            "error_types": {},
            "weight_distribution": [],
            "friction_distribution": [],
            "success_vs_failure": {"success": 0, "failure": 0}
        }

    # Count error types
    error_types = {}
    for run in simulation_runs:
        if not run['success']:
            error_type = run.get('error_type', 'unknown')
            error_types[error_type] = error_types.get(error_type, 0) + 1

    # Weight distribution (failures only)
    failures = [r for r in simulation_runs if not r['success']]
    weight_bins = [(0, 2), (2, 4), (4, 6), (6, 8)]
    weight_dist = []

    for start, end in weight_bins:
        count = sum(1 for f in failures if start <= f['object_weight'] < end)
        weight_dist.append({"range": f"{start}-{end}kg", "count": count})

    # Friction distribution
    friction_bins = [(0.1, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 0.9)]
    friction_dist = []

    for start, end in friction_bins:
        count = sum(1 for f in failures if start <= f['surface_friction'] < end)
        friction_dist.append({"range": f"{start}-{end}", "count": count})

    # Success vs Failure
    successes = sum(1 for r in simulation_runs if r['success'])

    return {
        "error_types": error_types,
        "weight_distribution": weight_dist,
        "friction_distribution": friction_dist,
        "success_vs_failure": {
            "success": successes,
            "failure": len(simulation_runs) - successes
        }
    }

# INSIGHTS GENERATION
@app.post("/api/generate-insights")
def generate_insights():
    """Generate AI insights from current failures"""
    try:
        failures = [r for r in simulation_runs if not r['success']]

        if len(failures) < 3:
            raise HTTPException(status_code=400, detail="Need at least 3 failures to analyze")

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

# EXPERIMENT RUNNER
@app.post("/api/experiments")
def create_experiment(request: ExperimentRequest):
    experiment_id = f"EXP_{uuid.uuid4().hex[:8]}"

    # Validate robot type
    if request.robot_type not in robot_configs:
        raise HTTPException(status_code=400, detail=f"Invalid robot type: {request.robot_type}")

    robot_config = robot_configs[request.robot_type]

    experiments[experiment_id] = {
        "id": experiment_id,
        "status": "running",
        "progress": 0,
        "total_runs": request.num_runs,
        "completed_runs": 0,
        "params": request.model_dump(),
        "robot_config": robot_config,
        "results": [],
        "started_at": datetime.now().isoformat()
    }

    def run_simulation_async():
        try:
            print(f"\n🚀 Starting experiment {experiment_id}")
            print(f"Robot: {robot_config['name']}")
            print(f"Attempting to import PickPlaceRobot...")

            from robot_pick_place import PickPlaceRobot
            import random

            print("✅ Import successful!")
            print(f"Creating robot simulator...")

            robot = PickPlaceRobot(gui=False, robot_type=request.robot_type)
            print("✅ Robot created!")

            results = []

            for i in range(request.num_runs):
                weight = request.object_weight if request.object_weight else random.uniform(0.3, robot_config['max_payload'])
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
                    "robot_type": request.robot_type,
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
        "message": f"Experiment started with {request.num_runs} runs on {robot_config['name']}"
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

        robot_type = run.get('robot_type', 'kuka_iiwa7')
        robot_config = robot_configs[robot_type]

        prompt = f"""Analyze this robotic simulation run briefly (3-4 sentences):
Run: {run['run_id']} - {'SUCCESS' if run['success'] else 'FAILURE'}
Robot: {robot_config['name']} (Max Force: {robot_config['max_gripper_force']}N, Payload: {robot_config['max_payload']}kg)
Weight: {run['object_weight']}kg, Friction: {run['surface_friction']}, Lighting: {run['lighting_variance']}
Error: {run.get('error_type', 'N/A')}

Explain the root cause and give one specific recommendation."""

        # Try Gemini 3 first, fallback to 2.5 if quota exceeded
        models_to_try = ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-1.5-flash"]
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                return {
                    "run_id": run_id,
                    "outcome": "success" if run['success'] else "failure",
                    "root_cause": response.text,
                    "model_used": model_name,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower():
                    print(f"⚠️ {model_name} quota exceeded, trying next model...")
                    continue
                else:
                    raise
        
        raise HTTPException(status_code=503, detail="All Gemini models quota exceeded")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/simulate-with-frames")
def simulate_with_frames(request: dict):
    """Run single simulation and return frames"""
    try:
        from robot_pick_place import PickPlaceRobot

        weight = request.get("weight", 0.8)
        friction = request.get("friction", 0.5)
        lighting = request.get("lighting", 0.5)
        robot_type = request.get("robot_type", "kuka_iiwa7")

        robot = PickPlaceRobot(gui=False, robot_type=robot_type)
        frames = robot.capture_simulation_frames(weight, friction, lighting)
        robot.close()

        return {"frames": frames}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Add custom robot endpoint
@app.post("/api/robots/custom")
def create_custom_robot(robot: dict):
    """Create custom robot configuration"""
    custom_id = f"custom_{uuid.uuid4().hex[:6]}"
    robot_configs[custom_id] = {
        "name": robot.get("name", "Custom Robot"),
        "description": robot.get("description", "User-defined robot"),
        "max_payload": float(robot.get("max_payload", 5.0)),
        "max_gripper_force": int(robot.get("max_gripper_force", 100)),
        "max_acceleration": float(robot.get("max_acceleration", 5.0)),
        "dof": int(robot.get("dof", 6)),
        "reach": int(robot.get("reach", 800)),
        "use_case": robot.get("use_case", "Custom application"),
        "urdf": "kuka_iiwa/model.urdf"  # Use Kuka model for visualization
    }
    return {"robot_id": custom_id, "config": robot_configs[custom_id]}


# Add custom robot endpoint
@app.post("/api/robots/custom")
def create_custom_robot(robot: dict):
    """Create custom robot configuration"""
    custom_id = f"custom_{uuid.uuid4().hex[:6]}"
    robot_configs[custom_id] = {
        "name": robot.get("name", "Custom Robot"),
        "description": robot.get("description", "User-defined robot"),
        "max_payload": float(robot.get("max_payload", 5.0)),
        "max_gripper_force": int(robot.get("max_gripper_force", 100)),
        "max_acceleration": float(robot.get("max_acceleration", 5.0)),
        "dof": int(robot.get("dof", 6)),
        "reach": int(robot.get("reach", 800)),
        "use_case": robot.get("use_case", "Custom application"),
        "urdf": "kuka_iiwa/model.urdf"  # Use Kuka model for visualization
    }
    return {"robot_id": custom_id, "config": robot_configs[custom_id]}

# Add custom robot endpoint
@app.post("/api/robots/custom")
def create_custom_robot(robot: dict):
    """Create custom robot configuration"""
    custom_id = f"custom_{uuid.uuid4().hex[:6]}"
    robot_configs[custom_id] = {
        "name": robot.get("name", "Custom Robot"),
        "description": robot.get("description", "User-defined robot"),
        "max_payload": float(robot.get("max_payload", 5.0)),
        "max_gripper_force": int(robot.get("max_gripper_force", 100)),
        "max_acceleration": float(robot.get("max_acceleration", 5.0)),
        "dof": int(robot.get("dof", 6)),
        "reach": int(robot.get("reach", 800)),
        "use_case": robot.get("use_case", "Custom application"),
        "urdf": "kuka_iiwa/model.urdf"  # Use Kuka model for visualization
    }
    return {"robot_id": custom_id, "config": robot_configs[custom_id]}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
