"""
FailSim AI - Gemini Pro Root Cause Analyzer
Sana's AI analysis code
"""

import google.generativeai as genai
import json
import os
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from backend/.env
env_path = Path(__file__).parent.parent.parent / 'backend' / '.env'
load_dotenv(env_path)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    print("⚠️  WARNING: GEMINI_API_KEY not set in backend/.env")
    print("   Get your key from: https://aistudio.google.com/app/apikey")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ Gemini API configured successfully")

def analyze_failure_cluster(failures: List[Dict]) -> Dict:
    """
    Analyze a cluster of failures using Gemini 2.5 Flash
    
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
    
    # Determine cluster name based on conditions
    cluster_name = "General failures"
    if avg_weight > 0.8 and avg_friction < 0.4:
        cluster_name = "Heavy object + low friction failures"
    elif avg_weight > 0.8:
        cluster_name = "Heavy object failures"
    elif avg_friction < 0.3:
        cluster_name = "Low friction failures"
    elif avg_lighting > 0.7:
        cluster_name = "High lighting variance failures"
    
    # Build prompt
    prompt = f"""
Analyze this pick & place robot failure pattern:

FAILURE CLUSTER: "{cluster_name}"

CONDITIONS:
- Object weight: {avg_weight:.2f} kg (average across {total_failures} failures)
- Surface friction coefficient: {avg_friction:.2f} (average)
- Lighting variance: {avg_lighting:.2f} (average)

OBSERVED FAILURES: {total_failures} runs

COMMON ERROR TYPES:
{json.dumps(error_types, indent=2)}

TASK:
You are a robotics failure analyst. Explain WHY the robot fails under these specific conditions.

1. Write 2-3 sentences explaining the ROOT CAUSE - why these environmental conditions lead to failure
2. Write 2-3 sentences explaining the FAILURE MECHANISM - what physical or control breakdown occurs

Be technical and specific. Reference the actual parameter values.

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:

**Root Cause:**
[Your 2-3 sentence explanation here]

**Failure Mechanism:**
[Your 2-3 sentence technical breakdown here]
"""
    
    try:
        # Call Gemini 2.5 Flash (latest stable model)
        print(f"\n🤖 Calling Gemini API...")
        print(f"   Model: gemini-3-flash-preview")
        print(f"   Analyzing {total_failures} failures...")
        
        model = genai.GenerativeModel('gemini-3-flash-preview')
        response = model.generate_content(prompt)
        
        print(f"✅ Gemini responded successfully")
        
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
        else:
            # Fallback if format is different
            root_cause = text.strip()
        
        result = {
            "cluster_name": cluster_name,
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
        
        return result
        
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return {
            "error": str(e),
            "cluster_name": "Analysis failed"
        }

def analyze_all_failures(backend_url=None):
    """
    Fetch failures from backend and analyze with Gemini
    """
    import requests
    
    if backend_url is None:
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    print(f"\n🔍 Fetching failures from backend: {backend_url}")
    
    try:
        response = requests.get(f"{backend_url}/api/runs/failures")
        data = response.json()
        failures = data.get("failures", [])
        
        if not failures:
            print("❌ No failures found in backend")
            print("   Run simulations first: cd simulation && python run_batch.py")
            return
        
        print(f"📊 Found {len(failures)} failures")
        
        # Analyze
        insight = analyze_failure_cluster(failures)
        
        if "error" in insight:
            print(f"❌ Analysis failed: {insight['error']}")
            return
        
        # Print results
        print("\n" + "="*70)
        print("🧠 GEMINI 2.5 FLASH ANALYSIS RESULTS")
        print("="*70)
        print(f"\n📌 Cluster: {insight['cluster_name']}")
        print(f"   Failures: {insight['failure_count']}")
        print(f"   Conditions: weight={insight['conditions']['avg_weight']}kg, "
              f"friction={insight['conditions']['avg_friction']}, "
              f"lighting={insight['conditions']['avg_lighting']}")
        print(f"\n💡 **Root Cause:**")
        print(f"   {insight.get('root_cause', 'N/A')}")
        print(f"\n⚙️  **Failure Mechanism:**")
        print(f"   {insight.get('failure_mechanism', 'N/A')}")
        print("\n" + "="*70)
        
        # Send insight back to backend
        try:
            resp = requests.post(f"{backend_url}/api/insights", json={
                "cluster_name": insight["cluster_name"],
                "failure_count": insight["failure_count"],
                "total_runs": len(failures),
                "percentage": 100.0,
                "root_cause": insight.get("root_cause", ""),
                "failure_mechanism": insight.get("failure_mechanism", "")
            })
            
            if resp.status_code == 200:
                print("✅ Insight saved to backend")
            else:
                print(f"⚠️  Could not save to backend: {resp.status_code}")
                
        except Exception as e:
            print(f"⚠️  Backend save failed: {e}")
        
        return insight
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to backend at {backend_url}")
        print("   Make sure backend is running: cd backend && python src/main.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    print("="*70)
    print("🚀 FailSim AI - Gemini 2.5 Flash Analyzer Test")
    print("="*70)
    
    # Check if API key is set
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        print("\n❌ ERROR: Gemini API key not configured")
        print("\nSteps to fix:")
        print("1. Go to: https://aistudio.google.com/app/apikey")
        print("2. Create an API key")
        print("3. Edit backend/.env and paste your key")
        print("4. Run this script again")
        sys.exit(1)
    
    # Test with sample data
    print("\n🧪 Testing with sample failure data...")
    
    sample_failures = [
        {
            "run_id": "run_001",
            "object_weight": 0.95,
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
        },
        {
            "run_id": "run_003",
            "object_weight": 0.88,
            "surface_friction": 0.22,
            "lighting_variance": 0.82,
            "error_type": "object_dropped"
        },
        {
            "run_id": "run_004",
            "object_weight": 1.05,
            "surface_friction": 0.30,
            "lighting_variance": 0.78,
            "error_type": "timeout"
        }
    ]
    
    result = analyze_failure_cluster(sample_failures)
    
    if "error" in result:
        print(f"\n❌ Test failed: {result['error']}")
        sys.exit(1)
    
    print("\n✅ TEST SUCCESSFUL!")
    print("\n📋 Full Response:")
    print(json.dumps(result, indent=2))
    
    print("\n" + "="*70)
    print("🎉 Gemini 2.5 Flash analyzer is working correctly!")
    print("\nNext steps:")
    print("1. Start backend: cd backend && python src/main.py")
    print("2. Run simulations: cd simulation && python run_batch.py")
    print("3. Analyze real failures: python ai/analysis/gemini_analyzer.py")
    print("="*70)
