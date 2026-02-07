"""
FailSim AI - Gemini Pro Root Cause Analyzer
Sana's AI analysis code
"""

import google.generativeai as genai
import json
import os
from typing import List, Dict

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your_key_here")
genai.configure(api_key=GEMINI_API_KEY)

def analyze_failure_cluster(failures: List[Dict]) -> Dict:
    """
    Analyze a cluster of failures using Gemini Pro
    
    Args:
        failures: List of failed simulation runs
        
    Returns:
        Dict with root_cause and failure_mechanism
    """
    
    if not failures:
        return {"error": "No failures to analyze"}
    
    # Calculate cluster statistics
    total_failures = len(failures)
    avg_weight = sum(f["object_weight"] for f in failures) / total_failures
    avg_friction = sum(f["surface_friction"] for f in failures) / total_failures
    avg_lighting = sum(f["lighting_variance"] for f in failures) / total_failures
    
    # Count error types
    error_types = {}
    for f in failures:
        error = f.get("error_type", "unknown")
        error_types[error] = error_types.get(error, 0) + 1
    
    # Build prompt
    prompt = f"""
Analyze this pick & place robot failure pattern:

FAILURE CLUSTER: "Heavy object + low friction failures"

CONDITIONS:
- Object weight: {avg_weight:.2f} kg (average)
- Surface friction: {avg_friction:.2f} (average)
- Lighting variance: {avg_lighting:.2f} (average)

OBSERVED FAILURES: {total_failures} runs

COMMON ERROR TYPES:
{json.dumps(error_types, indent=2)}

Task:
1. Explain in 2-3 sentences WHY the robot fails under these specific conditions
2. Identify the physical or algorithmic breakdown
3. Be specific about the failure mechanism

Format your response as:

**Root Cause:**
[Your explanation here]

**Failure Mechanism:**
[Technical breakdown]
"""
    
    try:
        # Call Gemini Pro
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Parse response
        text = response.text
        
        # Extract root cause and mechanism
        root_cause = ""
        failure_mechanism = ""
        
        if "**Root Cause:**" in text:
            parts = text.split("**Root Cause:**")
            if len(parts) > 1:
                cause_section = parts[1].split("**Failure Mechanism:**")
                root_cause = cause_section[0].strip()
                if len(cause_section) > 1:
                    failure_mechanism = cause_section[1].strip()
        
        return {
            "cluster_name": "Heavy object + low friction failures",
            "failure_count": total_failures,
            "conditions": {
                "avg_weight": round(avg_weight, 2),
                "avg_friction": round(avg_friction, 2),
                "avg_lighting": round(avg_lighting, 2)
            },
            "error_types": error_types,
            "root_cause": root_cause,
            "failure_mechanism": failure_mechanism,
            "raw_response": text
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "cluster_name": "Analysis failed"
        }

def analyze_all_failures(backend_url="http://localhost:8000"):
    """
    Fetch failures from backend and analyze with Gemini
    """
    import requests
    
    print("🧠 Fetching failures from backend...")
    
    try:
        response = requests.get(f"{backend_url}/api/runs/failures")
        data = response.json()
        failures = data.get("failures", [])
        
        if not failures:
            print("❌ No failures to analyze")
            return
        
        print(f"📊 Found {len(failures)} failures")
        print("🤖 Analyzing with Gemini Pro...")
        
        # Analyze
        insight = analyze_failure_cluster(failures)
        
        # Print results
        print("\n" + "="*60)
        print("🔍 GEMINI PRO ANALYSIS")
        print("="*60)
        print(f"\n**Root Cause:**\n{insight.get('root_cause', 'N/A')}")
        print(f"\n**Failure Mechanism:**\n{insight.get('failure_mechanism', 'N/A')}")
        print("\n" + "="*60)
        
        # Send insight back to backend
        requests.post(f"{backend_url}/api/insights", json={
            "cluster_name": insight["cluster_name"],
            "failure_count": insight["failure_count"],
            "total_runs": len(failures),
            "percentage": 100.0,  # Will calculate properly later
            "root_cause": insight.get("root_cause", ""),
            "failure_mechanism": insight.get("failure_mechanism", "")
        })
        
        print("✅ Insight saved to backend")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test with sample data
    sample_failures = [
        {
            "run_id": "run_001",
            "object_weight": 0.9,
            "surface_friction": 0.25,
            "lighting_variance": 0.8,
            "error_type": "object_dropped"
        },
        {
            "run_id": "run_002",
            "object_weight": 1.1,
            "surface_friction": 0.28,
            "lighting_variance": 0.75,
            "error_type": "placement_miss"
        }
    ]
    
    print("Testing Gemini analysis with sample data...\n")
    result = analyze_failure_cluster(sample_failures)
    print(json.dumps(result, indent=2))
