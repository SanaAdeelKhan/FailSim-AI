"""
FailSim AI - Batch Simulation Runner
Runs pick & place simulations with domain randomization
"""

import random
import json
import time
from datetime import datetime
import requests
import os

# Backend API endpoint (update when Ahmed deploys)
BACKEND_URL = "http://80.240.20.49:8000"

def simulate_pick_and_place(run_id, weight, friction, lighting):
    """
    Simulate a single pick & place run
    
    This is a PLACEHOLDER - Wajiha will replace with real PyBullet simulation
    For now, it generates realistic-looking fake data
    """
    
    # Simulate execution time (2-15 seconds)
    time_seconds = random.uniform(2.0, 15.0)
    
    # Failure probability increases with:
    # - Heavy objects (>0.8kg)
    # - Low friction (<0.3)
    # - High lighting variance (>0.7)
    
    failure_prob = 0.0
    
    if weight > 0.8:
        failure_prob += 0.3
    if friction < 0.3:
        failure_prob += 0.25
    if lighting > 0.7:
        failure_prob += 0.15
    
    # Random failure
    failed = random.random() < failure_prob
    
    # Determine error type if failed
    error_type = None
    dropped = False
    
    if failed:
        errors = ["object_dropped", "placement_miss", "timeout"]
        error_type = random.choice(errors)
        dropped = (error_type == "object_dropped")
    
    # Distance from target (worse if failed)
    if failed:
        distance = random.uniform(0.05, 0.20)  # 5-20cm off
    else:
        distance = random.uniform(0.0, 0.03)   # 0-3cm off
    
    return {
        "run_id": run_id,
        "success": not failed,
        "time_seconds": round(time_seconds, 2),
        "object_weight": weight,
        "surface_friction": friction,
        "lighting_variance": lighting,
        "distance_from_target": round(distance, 3),
        "dropped": dropped,
        "error_type": error_type,
        "timestamp": datetime.now().isoformat()
    }

def run_batch_simulations(num_runs=100):
    """Run batch of randomized simulations"""
    
    print(f"🤖 Starting {num_runs} pick & place simulations...")
    print(f"📡 Backend: {BACKEND_URL}")
    print("-" * 50)
    
    results = []
    
    for i in range(num_runs):
        # Domain randomization
        weight = random.uniform(0.3, 1.5)      # 0.3-1.5 kg
        friction = random.uniform(0.1, 0.8)    # 0.1-0.8 coefficient
        lighting = random.uniform(0.3, 1.0)    # 0.3-1.0 variance
        
        run_id = f"run_{i+1:04d}"
        
        # Run simulation
        result = simulate_pick_and_place(run_id, weight, friction, lighting)
        results.append(result)
        
        # Print progress
        status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
        print(f"{run_id}: {status} | w={weight:.2f}kg f={friction:.2f} l={lighting:.2f}")
    
    # Save to file (FIXED PATH)
    os.makedirs('outputs', exist_ok=True)
    output_file = f"outputs/batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("-" * 50)
    print(f"✅ Simulation complete!")
    print(f"📁 Results saved to: {output_file}")
    
    # Send to backend (if running)
    try:
        response = requests.post(f"{BACKEND_URL}/api/runs/batch", json=results)
        if response.status_code == 200:
            print(f"📤 Results sent to backend")
        else:
            print(f"⚠️  Backend error: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Could not connect to backend: {e}")
        print("   (This is OK if backend isn't running yet)")
    
    # Print statistics
    successes = sum(1 for r in results if r["success"])
    print(f"\n📊 Statistics:")
    print(f"   Total runs: {num_runs}")
    print(f"   Successes: {successes} ({successes/num_runs*100:.1f}%)")
    print(f"   Failures: {num_runs - successes} ({(num_runs-successes)/num_runs*100:.1f}%)")
    
    return results

if __name__ == "__main__":
    import sys
    
    # Get number of runs from command line or use default
    num_runs = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    run_batch_simulations(num_runs)
