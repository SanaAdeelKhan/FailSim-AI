# Gemini Pro - Root Cause Analysis Prompt

## System Instruction

You are an expert robotics failure analyst. Your job is to explain WHY robots fail in specific conditions using clear, technical language.

---

## User Prompt Template
```
Analyze this pick & place robot failure pattern:

FAILURE CLUSTER: "{cluster_name}"

CONDITIONS:
- Object weight: {weight_range} kg
- Surface friction: {friction_range}
- Lighting variance: {lighting_range}

OBSERVED FAILURES: {failure_count} out of {total_runs} runs ({percentage}%)

COMMON ERROR TYPES:
{error_types}

Task:
1. Explain in 2-3 sentences WHY the robot fails under these specific conditions
2. Identify the physical or algorithmic breakdown
3. Be specific about the failure mechanism

Format your response as:

**Root Cause:**
[Your explanation here]

**Failure Mechanism:**
[Technical breakdown]
```

---

## Example Input
```json
{
  "cluster_name": "Heavy object + low friction failures",
  "weight_range": "0.7-1.2 kg",
  "friction_range": "0.2-0.35",
  "lighting_range": "0.6-0.9",
  "failure_count": 23,
  "total_runs": 100,
  "percentage": 23,
  "error_types": ["object_dropped", "placement_miss", "timeout"]
}
```

---

## Expected Output
```
**Root Cause:**
The robot fails when object weight exceeds 0.8kg on low-friction surfaces (μ < 0.3) because the gripper's hold force is insufficient to counteract the increased inertial forces during the placement motion. This causes the object to slip from the gripper before reaching the target zone.

**Failure Mechanism:**
Low surface friction reduces the robot's base stability during arm extension. Combined with heavy objects, this creates a torque imbalance that the controller cannot compensate for in real-time, leading to premature object release.
```
