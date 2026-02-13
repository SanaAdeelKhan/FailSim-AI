import time
import json
from robot_100_simulation import RobotSim  # Imports your robot engine

def simulated_gemini_agent(failure_log):
    """
    This simulates Gemini analyzing the JSON data.
    In the real backend, this would be an API call.
    For the video, we print it to the screen so judges see it.
    """
    print("\n" + "="*40)
    print("🤖 GEMINI AGENT ACTIVATED")
    print("="*40)
    time.sleep(1) # Fake "thinking" time
    
    print(f"❌ ANALYZING FAILURE: {failure_log['error_type']}")
    print(f"📊 TELEMETRY: Friction={failure_log['friction']}, Mass={failure_log['object_mass']}")
    
    time.sleep(1.5)
    print("🧠 REASONING: The friction coefficient (0.1) is too low for the object mass.")
    print("💡 DECISION: Enabling 'High-Grip Mode' and increasing friction to 0.9.")
    print("="*40 + "\n")
    
    # The "Fix" parameters
    return {
        "friction": 0.9,
        "object_mass": 0.1,
        "lighting": 1.0
    }

def run_demo():
    # 1. SETUP THE SCENE
    # We turn render=True so we can RECORD this!
    sim = RobotSim(render=True)
    
    # ----------------------------------------
    # SCENE 1: THE FAILURE (The Problem)
    # ----------------------------------------
    print("\n🎬 SCENE 1: RUNNING WITH UNSTABLE CONFIGURATION...")
    bad_config = {
        "run_id": "demo_fail",
        "friction": 0.1,        # ICE! (Will cause slip)
        "object_mass": 0.1,
        "lighting": 0.5
    }
    
    result = sim.run_episode(bad_config)
    
    if not result['success']:
        print("💥 ROBOT FAILED AS EXPECTED.")
        
        # 2. THE AGENT (The Solution)
        # We pass the failure data to the "Agent"
        new_params = simulated_gemini_agent(result)
        
        # 3. THE FIX (The Result)
        print("🎬 SCENE 2: RE-RUNNING WITH AGENT FIX...")
        time.sleep(2) # Pause so you can read the text
        
        # Merge the new fix into the config
        fixed_config = bad_config.copy()
        fixed_config.update(new_params)
        fixed_config["run_id"] = "demo_fix"
        
        # Run again automatically
        fix_result = sim.run_episode(fixed_config)
        
        if fix_result['success']:
            print("\n✅ SELF-HEALING SUCCESSFUL!")
            print("The system automatically recovered from the failure.")
    else:
        print("⚠️ Weird, it succeeded by mistake? Try making friction lower!")

if __name__ == "__main__":
    run_demo()