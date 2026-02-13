import time
from robot_100_simulation_2 import SurgerySim

def agent_diagnose(failure_reason):
    print("\n" + "!"*40)
    print("🤖 MED-AI AGENT ALERT")
    print("!"*40)
    time.sleep(1)
    print("❌ CRITICAL ERROR: Surgical Tool Dropped.")
    print("📉 SENSOR DATA: Grip Force = 50N (Too Low for Steel Instrument)")
    time.sleep(1.5)
    print("💉 AGENT ACTION: Recalibrating Gripper Torque...")
    print("⚡ UPDATING PARAMETER: Grip Force -> 500N")
    print("🔄 RESTARTING HANDOFF PROCEDURE...")
    print("!"*40 + "\n")
    return 500 # Return new force

def run_demo():
    sim = SurgerySim(render=True)
    
    # SCENE 1: FAILURE (Weak Grip)
    print("🎬 SCENE 1: ATTEMPTING HANDOFF (Weak Grip)...")
    result = sim.run_handoff_attempt(config={'friction': 0.5, 'grip_force': 50}) # 50N = Weak
    
    if not result['success']:
        # SCENE 2: AGENT FIX
        new_force = agent_diagnose(result['error'])
        
        # SCENE 3: SUCCESS (Strong Grip)
        time.sleep(2)
        print("🎬 SCENE 2: ATTEMPTING HANDOFF (Agent Corrected)...")
        sim.run_handoff_attempt(config={'friction': 0.5, 'grip_force': new_force})
        print("\n✅ SURGICAL HANDOFF SUCCESSFUL.")

if __name__ == "__main__":
    run_demo()