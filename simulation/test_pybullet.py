"""
Test PyBullet Installation
Simple scene with falling cube
"""

import pybullet as p
import pybullet_data
import time

def test_pybullet():
    """Test PyBullet with simple falling cube"""
    
    print("🤖 Testing PyBullet...")
    
    # Connect to PyBullet with GUI
    physicsClient = p.connect(p.GUI)
    
    # Set up physics
    p.setAdditionalSearchPath(pybullet_data.getDataPath())
    p.setGravity(0, 0, -9.8)
    
    # Load ground plane
    planeId = p.loadURDF("plane.urdf")
    
    # Create a cube
    cubeStartPos = [0, 0, 1]
    cubeStartOrientation = p.getQuaternionFromEuler([0, 0, 0])
    
    # Create collision and visual shape
    cubeShape = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.05, 0.05, 0.05])
    cubeVisual = p.createVisualShape(p.GEOM_BOX, halfExtents=[0.05, 0.05, 0.05], rgbaColor=[1, 0, 0, 1])
    
    # Create multi-body (cube with mass)
    cubeId = p.createMultiBody(
        baseMass=1,
        baseCollisionShapeIndex=cubeShape,
        baseVisualShapeIndex=cubeVisual,
        basePosition=cubeStartPos,
        baseOrientation=cubeStartOrientation
    )
    
    print("✅ Scene created!")
    print("   - Ground plane loaded")
    print("   - Red cube created at height 1m")
    print("   - Gravity enabled")
    print("\n🎬 Running simulation for 5 seconds...")
    print("   Watch the cube fall!\n")
    
    # Run simulation
    for i in range(500):  # 5 seconds at 100Hz
        p.stepSimulation()
        time.sleep(1./100.)
        
        # Print cube position every second
        if i % 100 == 0:
            pos, orn = p.getBasePositionAndOrientation(cubeId)
            print(f"   Time {i/100:.1f}s: Cube height = {pos[2]:.3f}m")
    
    print("\n✅ PyBullet test successful!")
    print("🎯 You should see:")
    print("   - A 3D window opened")
    print("   - Red cube fell and landed on ground")
    print("   - Physics simulation working!")
    
    # Keep window open
    print("\n⏸️  Window will stay open for 3 seconds...")
    time.sleep(3)
    
    # Disconnect
    p.disconnect()
    print("✅ Test complete!")

if __name__ == "__main__":
    test_pybullet()
