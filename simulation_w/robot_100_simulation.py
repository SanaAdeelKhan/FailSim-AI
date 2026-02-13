import pybullet as p
import pybullet_data
import time
import random
import json

class RobotSim:
    def __init__(self, render=False):
        self.render = render
        if render:
            self.physicsClient = p.connect(p.GUI)
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
        else:
            self.physicsClient = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())

    def run_batch(self, num_runs=50):
        print(f"🚀 Starting {num_runs} simulations (Magic Grip Enabled)...")
        results = []
        
        for i in range(num_runs):
            # RANDOMIZE: Mix of "Sticky" (Success) and "Slippery" (Fail)
            config = {
                "run_id": f"run_{i:03d}",
                # If friction > 0.4, Magic Grip activates. If < 0.4, it fails.
                "friction": round(random.uniform(0.1, 0.9), 2), 
                "object_mass": round(random.uniform(0.1, 1.0), 2),
                "lighting": round(random.uniform(0.5, 1.0), 2)
            }
            
            metrics = self.run_episode(config)
            results.append(metrics)
            
            status = "✅ SUCCESS" if metrics['success'] else "❌ FAILED"
            print(f"Run {i}: {status} (Friction: {config['friction']})")
            
        with open("simulation_data.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\n💾 Data saved to 'simulation_data.json'")
        p.disconnect()

    def run_episode(self, config):
        p.resetSimulation()
        p.setGravity(0, 0, -9.8)
        
        # SETUP
        p.loadURDF("plane.urdf")
        robotId = p.loadURDF("franka_panda/panda.urdf", useFixedBase=True)
        cubeId = p.loadURDF("cube_small.urdf", [0.5, 0, 0.05])
        
        # MOVEMENT PHASES
        # 1. Hover, 2. Lower, 3. Grasp (Trigger Magic), 4. Lift
        phases = [
            {"pos": [0.5, 0, 0.5], "grip": 0.08, "steps": 20}, # Hover
            {"pos": [0.5, 0, 0.05], "grip": 0.08, "steps": 40}, # Lower
            {"pos": [0.5, 0, 0.05], "grip": 0.0,  "steps": 40, "action": "grasp"}, # GRASP!
            {"pos": [0.5, 0, 0.5], "grip": 0.0,  "steps": 60}, # Lift
        ]
        
        constraint_id = None # The "Magic Glue" ID

        for phase in phases:
            for _ in range(phase["steps"]):
                p.stepSimulation()
                
                # Move Arm
                poses = p.calculateInverseKinematics(robotId, 11, phase["pos"])
                for i in range(7):
                    p.setJointMotorControl2(robotId, i, p.POSITION_CONTROL, poses[i])
                
                # Move Gripper
                p.setJointMotorControl2(robotId, 9, p.POSITION_CONTROL, phase["grip"]/2, force=500)
                p.setJointMotorControl2(robotId, 10, p.POSITION_CONTROL, phase["grip"]/2, force=500)

                # --- THE MAGIC TRICK ---
                # If we are in "grasp" phase AND friction is good (> 0.4), lock the cube!
                if "action" in phase and phase["action"] == "grasp" and constraint_id is None:
                    if config["friction"] > 0.4: 
                        # Create a "Fixed Joint" between gripper and cube (Magic Glue)
                        constraint_id = p.createConstraint(robotId, 9, cubeId, -1, p.JOINT_FIXED, [0, 0, 0], [0, 0, 0], [0, 0, 0])
                
                if self.render: time.sleep(1./240.)

        # CHECK SUCCESS
        cube_z = p.getBasePositionAndOrientation(cubeId)[0][2]
        success = cube_z > 0.4
        
        return {
            **config,
            "success": success,
            "error_type": "Slip" if not success else None,
            "final_height": round(cube_z, 2)
        }

if __name__ == "__main__":
    # render=False -> Fast Data Generation
    sim = RobotSim(render=False) 
    sim.run_batch(num_runs=100)