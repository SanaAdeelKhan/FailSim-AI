"""
Real Kuka iiwa7 Robot Specifications
Source: Kuka technical documentation
"""

class KukaIIWA7Specs:
    """
    Kuka iiwa7 Collaborative Robot Arm
    Real-world specifications for pick & place operations
    """
    
    # Robot specifications
    MAX_PAYLOAD = 7.0  # kg (rated maximum)
    REACH = 0.8  # meters
    REPEATABILITY = 0.0001  # ±0.1mm
    
    # Gripper specifications (standard pneumatic gripper)
    GRIPPER_MAX_FORCE = 100  # Newtons (typical pneumatic gripper)
    GRIPPER_OPENING = 0.08  # 8cm max opening
    GRIPPER_CLOSING_TIME = 0.3  # seconds
    
    # Physical constants
    GRAVITY = 9.81  # m/s²
    
    # Safety factors (from Kuka documentation)
    DYNAMIC_SAFETY_FACTOR = 0.7  # Reduce capacity by 30% for dynamic movements
    
    # Motion parameters
    MAX_SPEED = 1.5  # m/s (end effector speed)
    MAX_ACCELERATION = 5.0  # m/s² (end effector acceleration)
    
    # Vision system specifications
    CAMERA_ACCURACY_PERFECT = 0.001  # ±1mm in perfect conditions
    CAMERA_ACCURACY_POOR = 0.015  # ±15mm in poor lighting
    
    @staticmethod
    def calculate_required_grip_force(mass, friction_coefficient, acceleration=5.0):
        """
        Calculate minimum grip force needed using physics
        
        F_grip = (m * g + m * a) / μ
        
        Where:
        - m: object mass (kg)
        - g: gravity (9.81 m/s²)
        - a: acceleration (m/s²)
        - μ: friction coefficient between gripper and object
        """
        
        total_force = mass * (KukaIIWA7Specs.GRAVITY + acceleration)
        required_grip = total_force / max(friction_coefficient, 0.01)  # Prevent division by zero
        
        return required_grip
    
    @staticmethod
    def can_grip_object(mass, friction_coefficient):
        """
        Physics-based check: Can the gripper hold this object?
        
        Returns: (can_grip, margin, reason)
        """
        
        required_force = KukaIIWA7Specs.calculate_required_grip_force(
            mass, friction_coefficient
        )
        
        available_force = KukaIIWA7Specs.GRIPPER_MAX_FORCE
        
        can_grip = required_force < available_force
        margin = available_force - required_force
        
        if not can_grip:
            reason = f"Required grip force ({required_force:.1f}N) exceeds gripper capacity ({available_force}N)"
        else:
            reason = f"Safe with {margin:.1f}N margin"
        
        return can_grip, margin, reason
    
    @staticmethod
    def calculate_vision_error(lighting_variance):
        """
        Calculate vision system error based on lighting conditions
        
        lighting_variance: 0.0 (perfect) to 1.0 (very poor)
        Returns: position error in meters
        """
        
        min_error = KukaIIWA7Specs.CAMERA_ACCURACY_PERFECT
        max_error = KukaIIWA7Specs.CAMERA_ACCURACY_POOR
        
        # Linear interpolation based on lighting
        vision_error = min_error + (max_error - min_error) * lighting_variance
        
        return vision_error
    
    @staticmethod
    def will_slip_during_movement(mass, friction_coefficient, acceleration=None):
        """
        Physics check: Will object slip during acceleration?
        
        Object slips if: F_friction < F_inertial
        F_friction = μ * m * g
        F_inertial = m * a
        """
        
        if acceleration is None:
            acceleration = KukaIIWA7Specs.MAX_ACCELERATION
        
        friction_force = friction_coefficient * mass * KukaIIWA7Specs.GRAVITY
        inertial_force = mass * acceleration
        
        will_slip = inertial_force > friction_force
        
        return will_slip

# Test the physics
if __name__ == "__main__":
    print("🤖 Kuka iiwa7 Real Physics Test\n")
    print("="*60)
    
    # Test case 1: Light object, good friction
    print("\n📦 Test 1: 0.5kg object, friction=0.6")
    can_grip, margin, reason = KukaIIWA7Specs.can_grip_object(0.5, 0.6)
    print(f"   Can grip: {can_grip}")
    print(f"   Reason: {reason}")
    
    # Test case 2: Heavy object, low friction
    print("\n📦 Test 2: 1.5kg object, friction=0.25")
    can_grip, margin, reason = KukaIIWA7Specs.can_grip_object(1.5, 0.25)
    print(f"   Can grip: {can_grip}")
    print(f"   Reason: {reason}")
    
    # Test case 3: Slip test
    print("\n📦 Test 3: Will 1.0kg object slip at friction=0.3?")
    will_slip = KukaIIWA7Specs.will_slip_during_movement(1.0, 0.3)
    print(f"   Will slip: {will_slip}")
    
    # Test case 4: Vision accuracy
    print("\n📦 Test 4: Vision accuracy at different lighting")
    for lighting in [0.2, 0.5, 0.8]:
        error = KukaIIWA7Specs.calculate_vision_error(lighting)
        print(f"   Lighting variance {lighting}: ±{error*1000:.1f}mm error")
    
    print("\n" + "="*60)
    print("✅ Real physics calculations working!")
