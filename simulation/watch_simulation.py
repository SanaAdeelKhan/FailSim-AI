"""
Visual Demo - Watch the robot simulation in action!
Better camera, longer viewing time, clearer view
"""

import pybullet as p
from robot_pick_place import PickPlaceRobot
from robot_specs import KukaIIWA7Specs
import time

def watch_demo_enhanced():
    """Watch simulation with better camera and timing"""
    
    print("🎬 Starting Enhanced Visual Demo")
    print("="*60)
    print("3D window will open with close-up view of robot")
    print("="*60)
    
    # Create robot WITH GUI
    robot = PickPlaceRobot(gui=True)
    
    # BETTER CAMERA POSITION - Closer view!
    p.resetDebugVisualizerCamera(
        cameraDistance=1.2,        # Closer!
        cameraYaw=45,              # Angle
        cameraPitch=-20,           # Look down slightly
        cameraTargetPosition=[0.4, 0.1, 0.5]  # Focus on robot area
    )
    
    # Test multiple scenarios
    test_cases = [
        ("✅ EASY - Should succeed", 0.5, 0.7, 0.3, 8),
        ("⚠️ MEDIUM - Might slip", 0.9, 0.35, 0.4, 10),
        ("❌ HARD - Will fail", 1.2, 0.25, 0.6, 10),
    ]
    
    for name, weight, friction, lighting, duration in test_cases:
        print(f"\n{'='*60}")
        print(f"📦 {name}")
        print(f"   Weight: {weight}kg | Friction: {friction} | Lighting: {lighting}")
        
        # Physics prediction
        can_grip, margin, reason = KukaIIWA7Specs.can_grip_object(weight, friction)
        will_slip = KukaIIWA7Specs.will_slip_during_movement(weight, friction)
        
        print(f"\n🔬 Physics Prediction:")
        print(f"   • {reason}")
        print(f"   • Will slip during movement: {will_slip}")
        
        print(f"\n🎬 Running simulation...")
        print(f"   Watch the 3D window for {duration} seconds!")
        
        # Run simulation
        success, time_taken, dist_error, error_type, dropped = robot.simulate_pick_place(
            weight, friction, lighting
        )
        
        # Show results
        print(f"\n📊 Result:")
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"   Outcome: {status}")
        if error_type:
            print(f"   Error type: {error_type}")
            print(f"   Dropped: {dropped}")
        print(f"   Distance error: {dist_error*1000:.1f}mm")
        
        # Keep window open longer
        print(f"\n⏸️  Paused for {duration} seconds (you can rotate view with mouse)")
        time.sleep(duration)
        
        if test_cases.index((name, weight, friction, lighting, duration)) < len(test_cases) - 1:
            print("\n   → Next scenario loading...")
            time.sleep(2)
    
    print("\n" + "="*60)
    print("✅ Demo complete!")
    print("   Window will stay open for 10 more seconds")
    time.sleep(10)
    
    robot.close()

if __name__ == "__main__":
    watch_demo_enhanced()
