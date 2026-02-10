"""
FailSim AI - Real PyBullet Batch Runner
Runs pick & place simulations with domain randomization
"""

import random
import json
from datetime import datetime
import requests
import os
import sys

# Import real PyBullet simulation
try:
    from robot_pick_place import PickPlaceRobot
    REAL_SIM = True
    print("✅ Using REAL PyBullet robot simulation")
except ImportError:
    REAL_SIM = False
    print("⚠️  PyBullet not found - install with: pip install pybullet")
    sys.exit(1)

BACKEND_URL = "http://80.240.20.49:8000"

def run_batch_simulations(num_runs=100):
    """Run batch of randomized simulations with REAL robot"""
    
    print(f"🤖 Starting {num_runs} REAL pick & place simulations...")
    print(f"📡 Backend: {BACKEND_URL}")
    print(f"🔧 Simulation: PyBullet Physics Engine")
    print("-" * 50)
    
    # Initialize REAL robot simulator
    robot = PickPlaceRobot(gui=False)  # Headless for speed
    
    results = []
    
    for i in range(num_runs):
        # Domain randomization
        weight = random.uniform(0.3, 1.5)      # 0.3-1.5 kg
        friction = random.uniform(0.1, 0.8)    # 0.1-0.8 coefficient
        lighting = random.uniform(0.3, 1.0)    # 0.3-1.0 variance
        
        run_id = f"run_{i+1:04d}"
        
        # Run REAL simulation with physics
        success, time_sec, dist_error, error_type, dropped = robot.simulate_pick_place(
            weight, friction, lighting
        )
        
        result = {
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
        
        results.append(result)
        
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{run_id}: {status} | w={weight:.2f}kg f={friction:.2f} l={lighting:.2f}")
    
    # Close robot simulator
    robot.close()
    
    # Save results
    os.makedirs('outputs', exist_ok=True)
    output_file = f"outputs/batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("-" * 50)
    print(f"✅ Simulation complete!")
    print(f"📁 Results: {output_file}")
    
    # Send to backend
    try:
        response = requests.post(f"{BACKEND_URL}/api/runs/batch", json=results)
        if response.status_code == 200:
            print(f"📤 Data sent to Vultr backend")
    except Exception as e:
        print(f"⚠️  Backend connection failed: {e}")
    
    # Stats
    successes = sum(1 for r in results if r["success"])
    print(f"\n📊 Statistics:")
    print(f"   Total: {num_runs}")
    print(f"   Success: {successes} ({successes/num_runs*100:.1f}%)")
    print(f"   Failures: {num_runs - successes}")
    
    return results

if __name__ == "__main__":
    num_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    run_batch_simulations(num_runs)
