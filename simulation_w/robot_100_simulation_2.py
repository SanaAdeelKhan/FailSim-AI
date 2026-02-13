import pybullet as p
import pybullet_data
import time
import random

class SurgerySim:
    def __init__(self, render=False):
        self.render = render
        if render:
            self.physicsClient = p.connect(p.GUI)
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
            p.configureDebugVisualizer(p.COV_ENABLE_SHADOWS, 1) # Good lighting
            
            # CAMERA: Zoomed in on the "Operating Table"
            p.resetDebugVisualizerCamera(cameraDistance=1.0, cameraYaw=50, cameraPitch=-30, cameraTargetPosition=[0.5, 0, 0.2])
        else:
            self.physicsClient = p.connect(p.DIRECT)
            
        p.setAdditionalSearchPath(pybullet_data.getDataPath())

    def run_handoff_attempt(self, config):
        p.resetSimulation()
        p.setGravity(0, 0, -9.8)
        
        # --- 1. THE OPERATING ROOM (Visuals) ---
        # Make the floor "Sterile Blue"
        planeId = p.loadURDF("plane.urdf")
        p.changeVisualShape(planeId, -1, rgbaColor=[0.8, 0.9, 1.0, 1]) 

        # --- 2. THE SURGICAL ROBOT ---
        # Make it White (Medical Grade)
        robotId = p.loadURDF("franka_panda/panda.urdf", useFixedBase=True)
        for i in range(7):
            p.changeVisualShape(robotId, i, rgbaColor=[1, 1, 1, 1]) 

        # --- 3. THE "SCISSORS" (Object) ---
        # We use a small block to represent a "Sterile Tool Container"
        # (Simulating complex scissor geometry is unstable, boxes are safe!)
        toolStartPos = [0.5, 0, 0.05] 
        toolId = p.loadURDF("cube_small.urdf", toolStartPos)
        p.changeVisualShape(toolId, -1, rgbaColor=[0.8, 0.1, 0.1, 1]) # Red = Hazardous/Sharp
        p.changeDynamics(toolId, -1, mass=0.1, lateralFriction=config['friction'])

        # --- HEADS UP DISPLAY (HUD) ---
        if self.render:
            p.addUserDebugText("🏥 SURGICAL ASSISTANT AI", [-0.2, 0, 0.8], [0, 0, 0], textSize=1.5)
            status_color = [1, 0, 0] if config['grip_force'] < 100 else [0, 0.6, 0]
            p.addUserDebugText(f"GRIP FORCE: {config['grip_force']}N", [0.3, 0, 0.5], status_color, textSize=1.2)

        # --- HANDOFF ANIMATION ---
        phases = [
            {"pos": [0.5, 0, 0.4], "grip": 0.08, "steps": 40}, # Approach
            {"pos": [0.5, 0, 0.05], "grip": 0.08, "steps": 60}, # Lower to Tray
            {"pos": [0.5, 0, 0.05], "grip": 0.0,  "steps": 50, "action": "grasp"}, # GRASP
            {"pos": [0.5, 0, 0.5], "grip": 0.0,  "steps": 80}, # Handover to Doctor (Lift)
        ]
        
        constraint_id = None

        for phase in phases:
            for _ in range(phase["steps"]):
                p.stepSimulation()
                
                # Robot Control
                poses = p.calculateInverseKinematics(robotId, 11, phase["pos"])
                for i in range(7):
                    p.setJointMotorControl2(robotId, i, p.POSITION_CONTROL, poses[i])
                
                # Apply Configurable Grip Force
                force = config['grip_force']
                p.setJointMotorControl2(robotId, 9, p.POSITION_CONTROL, phase["grip"]/2, force=force)
                p.setJointMotorControl2(robotId, 10, p.POSITION_CONTROL, phase["grip"]/2, force=force)

                # "Magic Grasp" Logic (Physics Helper)
                if "action" in phase and phase["action"] == "grasp" and constraint_id is None:
                    # If force is high enough, lock it. If low, let it slip.
                    if config['grip_force'] > 200: 
                        constraint_id = p.createConstraint(robotId, 9, toolId, -1, p.JOINT_FIXED, [0, 0, 0], [0, 0, 0], [0, 0, 0])
                        p.addUserDebugText("🔒 LOCKED", [0.5, 0, 0.2], [0, 1, 0])
                
                if self.render: time.sleep(1./240.)

        # Check Result
        tool_z = p.getBasePositionAndOrientation(toolId)[0][2]
        success = tool_z > 0.3
        
        return {"success": success, "error": "Tool Dropped" if not success else None}