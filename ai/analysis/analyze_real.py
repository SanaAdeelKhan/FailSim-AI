"""
Analyze real failures from backend and post insights
"""
import requests
import json
import os
from gemini_analyzer import analyze_failure_cluster

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def analyze_and_post():
    print("🔍 Fetching failures from backend...")
    
    # Get all runs
    response = requests.get(f"{BACKEND_URL}/api/runs")
    runs = response.json()
    
    if not runs:
        print("❌ No runs found")
        return
    
    # Filter failures
    failures = [r for r in runs if not r['success']]
    print(f"Found {len(failures)} failures out of {len(runs)} total runs")
    
    if len(failures) < 3:
        print("⚠️  Need at least 3 failures for analysis")
        return
    
    # Analyze
    print(f"🧠 Analyzing with Gemini 3 Flash...")
    result = analyze_failure_cluster(failures)
    
    if result:
        # Post to backend
        insight_data = {
            "cluster_name": result["cluster_name"],
            "failure_count": result["failure_count"],
            "total_runs": len(runs),
            "percentage": (result["failure_count"] / len(runs)) * 100,
            "root_cause": result["root_cause"],
            "failure_mechanism": result["failure_mechanism"]
        }
        
        post_response = requests.post(
            f"{BACKEND_URL}/api/insights",
            json=insight_data
        )
        
        if post_response.status_code == 200:
            print("✅ Insight posted to backend successfully!")
            print(f"📊 Cluster: {result['cluster_name']}")
            print(f"💡 Root Cause: {result['root_cause'][:100]}...")
        else:
            print(f"❌ Failed to post insight: {post_response.status_code}")
    else:
        print("❌ Analysis failed")

if __name__ == "__main__":
    analyze_and_post()
