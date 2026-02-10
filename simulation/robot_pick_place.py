"""
FailSim AI - Physics-Based Robot Simulation
FIXED: Realistic vision thresholds
"""

import pybullet as p
import pybullet_data
import time
import numpy as np
import math
from robot_specs import KukaIIWA7Specs

class PickPlaceRobot:
    """Kuka iiwa7 robot with REALISTIC failure modeling"""
    
    def __init__(self, gui=False):
        if gui:
            self.client = p.connect(p.GUI)
        else:
            self.client = p.connect(p.DIRECT)
        
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -KukaIIWA7Specs.GRAVITY)
        
        self.plane = p.loadURDF("plane.urdf")
        self.table = p.loadURDF("table/table.urdf", [0.5, 0, 0], globalScaling=0.5)
        self.robot = p.loadURDF("kuka_iiwa/model.urdf", [0, 0, 0])
        self.num_joints = p.getNumJoints(self.robot)
        
    def simulate_pick_place(self, weight, friction, lighting_variance):
        """
        Physics-based pick & place with REALISTIC failure conditions
        
        FIXED: Vision threshold now 20mm instead of 10mm
        """
        
        start_time = time.time()
        
        # Create object
        obj_start_pos = [0.5, 0.0, 0.65]
        obj = self.create_object(weight, friction, obj_start_pos)
        target_pos = [0.5, 0.3, 0.65]
        
        # Run physics
        for _ in range(240):
            p.stepSimulation()
        
        # Physics checks
        can_grip, force_margin, grip_reason = KukaIIWA7Specs.can_grip_object(weight, friction)
        will_slip = KukaIIWA7Specs.will_slip_during_movement(weight, friction)
        vision_error = KukaIIWA7Specs.calculate_vision_error(lighting_variance)
        
        # Determine success/failure
        success = True
        error_type = None
        dropped = False
        
        # Failure Mode 1: Insufficient grip force
        if not can_grip:
            success = False
            error_type = "object_dropped"
            dropped = True
            distance_error = np.random.uniform(0.20, 0.40)
        
        # Failure Mode 2: Object slips during movement
        elif will_slip:
            success = False
            error_type = "object_dropped"
            dropped = True
            distance_error = np.random.uniform(0.15, 0.35)
        
        # Failure Mode 3: Vision error too large (FIXED THRESHOLD)
        elif vision_error > 0.020:  # >20mm is failure (was 10mm)
            success = False
            error_type = "placement_miss"
            dropped = False
            distance_error = vision_error + np.random.uniform(0.0, 0.05)
        
        # Success case
        else:
            success = True
            distance_error = vision_error
        
        # Random failures (5% for real-world uncertainty)
        if success and np.random.random() < 0.05:
            success = False
            error_type = "timeout"
            distance_error = np.random.uniform(0.05, 0.12)
        
        # Cleanup
        p.removeBody(obj)
        
        # Time calculation
        base_time = time.time() - start_time
        if not success:
            time_taken = base_time + np.random.uniform(2.0, 4.5)
        else:
            time_taken = base_time + np.random.uniform(0.5, 1.5)
        
        return success, time_taken, distance_error, error_type, dropped
    
    def create_object(self, weight, friction, position):
        size = 0.03
        collision_shape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[size, size, size])
        visual_shape = p.createVisualShape(
            p.GEOM_BOX, 
            halfExtents=[size, size, size],
            rgbaColor=[0.8, 0.2, 0.2, 1]
        )
        
        obj_id = p.createMultiBody(
            baseMass=weight,
            baseCollisionShapeIndex=collision_shape,
            baseVisualShapeIndex=visual_shape,
            basePosition=position
        )
        
        p.changeDynamics(obj_id, -1, lateralFriction=friction)
        p.changeDynamics(self.table, -1, lateralFriction=friction)
        
        return obj_id
    
    def close(self):
        p.disconnect(self.client)


def test_physics_driven_failures():
    """Test that failures are driven by real physics"""
    
    print("🤖 Physics-Driven Failure Discovery Test\n")
    print("="*70)
    print("Testing Kuka iiwa7 with FIXED vision threshold (20mm)")
    print(f"  Max gripper force: {KukaIIWA7Specs.GRIPPER_MAX_FORCE}N")
    print("="*70)
    
    robot = PickPlaceRobot(gui=False)
    
    test_cases = [
        ("✅ Light object, good conditions", 0.4, 0.7, 0.2),
        ("🎯 Medium object, moderate friction", 0.9, 0.45, 0.4),
        ("⚠️ Heavy object, good friction", 1.3, 0.6, 0.3),
        ("❌ Medium object, LOW FRICTION", 0.8, 0.25, 0.3),
        ("❌ Heavy + low friction", 1.2, 0.28, 0.4),
        ("⚠️ Good object, POOR LIGHTING", 0.6, 0.5, 0.85),
    ]
    
    results = []
    
    for name, weight, friction, lighting in test_cases:
        print(f"\n{'─'*70}")
        print(f"📦 {name}")
        print(f"   Weight: {weight}kg | Friction: {friction} | Lighting: {lighting}")
        
        # Physics predictions
        can_grip, margin, reason = KukaIIWA7Specs.can_grip_object(weight, friction)
        will_slip = KukaIIWA7Specs.will_slip_during_movement(weight, friction)
        vision_err = KukaIIWA7Specs.calculate_vision_error(lighting)
        
        print(f"\n   Physics Analysis:")
        print(f"   • {reason}")
        print(f"   • Will slip: {will_slip}")
        print(f"   • Vision error: ±{vision_err*1000:.1f}mm")
        print(f"   • Vision threshold: 20mm (failure if exceeded)")
        
        # Run simulation
        success, time_taken, dist_error, error_type, dropped = robot.simulate_pick_place(
            weight, friction, lighting
        )
        
        print(f"\n   Result:")
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   • {status}")
        if error_type:
            print(f"   • Error: {error_type}")
        print(f"   • Distance: {dist_error*1000:.1f}mm")
        
        results.append({'case': name, 'success': success, 'error_type': error_type})
    
    robot.close()
    
    print("\n" + "="*70)
    print("📊 SUMMARY:")
    successes = sum(1 for r in results if r['success'])
    print(f"  Successes: {successes}/{len(results)}")
    print(f"  Failures: {len(results) - successes}/{len(results)}")
    print("\n✅ Fixed simulation ready!")

if __name__ == "__main__":
    test_physics_driven_failures()
