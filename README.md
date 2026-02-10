# FailSim AI ⚡

**Automatic Failure Discovery & Root-Cause Analysis for Robotics — Before Hardware Exists**

[![Live Demo](https://img.shields.io/badge/Demo-Live-success)](http://80.240.20.49)
[![Backend](https://img.shields.io/badge/Backend-Vultr-blue)](http://80.240.20.49:8000)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚨 The Problem

Robotics companies generate **massive amounts of simulation data** during testing, but struggle to understand:
- Which combinations of factors cause failures?
- What are the root physical causes?
- How to prioritize fixes?

**Traditional approach:**
- ❌ Engineer manually reviews logs
- ❌ Slow, expensive, error-prone
- ❌ Miss subtle patterns

**FailSim AI approach:**
- ✅ Automated batch testing with real physics
- ✅ AI-powered root cause analysis
- ✅ Actionable engineering insights

---

## 💡 Our Solution

**FailSim AI** is a physics-based simulation platform that automatically discovers failure patterns and uses Gemini AI to explain WHY robots fail.

### Real-World Use Case

**Company:** Warehouse automation startup  
**Robot:** Kuka iiwa7 collaborative arm  
**Challenge:** Pick & place fails unpredictably in production

**Before FailSim AI:**
> "Our robot fails sometimes. Let's manually test 100 combinations and guess why."  
> **Cost:** 2 weeks, $10K in engineer time

**With FailSim AI:**
> "Run 1000 simulations overnight. FailSim AI reports: 'Failures occur when required grip force exceeds 100N (weight > 1.1kg AND friction < 0.32) because gripper slip torque exceeds motor capacity during acceleration. Recommendation: Add 15% grip force or use textured pads.'"  
> **Cost:** 1 day, automated

---

## 🤖 What FailSim AI Does

### 1. **Physics-Based Simulation**
- Real Kuka iiwa7 robot specifications (100N gripper force, 7kg payload)
- Actual physics equations (F = ma, friction laws, torque calculations)
- PyBullet 3D physics engine
- Domain randomization: object weight (0.3-1.5kg), surface friction (0.1-0.8), lighting variance (0.3-1.0)

### 2. **Automatic Failure Discovery**
- Runs 100s-1000s of simulations
- Detects failures based on real physics constraints:
  - **Gripper force insufficient:** F_required > F_max (100N)
  - **Object slips:** F_friction < F_inertial during acceleration
  - **Vision error:** Poor lighting degrades pose estimation

### 3. **AI-Powered Root Cause Analysis (Gemini 2.5 Flash)**
- Analyzes failure clusters
- Generates human-readable explanations
- Identifies physical mechanisms
- Provides engineering recommendations

### Example AI Insight:

> **Root Cause:**  
> "The robot fails when required grip force exceeds 100N, occurring at objects > 1.01kg with friction < 0.46. High lighting variance (0.68) degrades vision system accuracy."
> 
> **Failure Mechanism:**  
> "Gripper clamping force is overcome by inertial forces during dynamic movements (10 drops). Vision errors cause incorrect placement targets (26 placement misses)."
> 
> **Recommended Fixes:**
> 1. Increase gripper force threshold by 20% for objects >0.8kg
> 2. Implement adaptive lighting compensation in vision pipeline
> 3. Test with textured gripper pads to increase friction coefficient

---

## 🏗️ Architecture
```
┌─────────────────┐
│   PyBullet      │  Real Physics Simulation
│   Kuka iiwa7    │  • 100N gripper force
│                 │  • Gravity, friction, collisions
└────────┬────────┘
         │
         │ Simulation Results (JSON)
         ▼
┌─────────────────┐
│  Vultr Backend  │  Central System of Record
│  FastAPI        │  • Stores all run data
│  Port 8000      │  • Serves REST API
└────────┬────────┘
         │
         │ Failure Data
         ▼
┌─────────────────┐
│  Gemini 2.5     │  AI Analysis
│  Flash          │  • Clusters failures
│                 │  • Explains root causes
└────────┬────────┘
         │
         │ AI Insights
         ▼
┌─────────────────┐
│  React          │  Web Dashboard
│  Dashboard      │  • Success/failure charts
│  Port 80        │  • AI explanations
└─────────────────┘
```

**Tech Stack:**
- **Simulation:** PyBullet (physics), Python 3.10
- **Backend:** FastAPI, Vultr VM (Frankfurt)
- **AI:** Google Gemini 2.5 Flash API
- **Frontend:** React, Tailwind CSS, Nginx
- **Deployment:** All-in-one Vultr server

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip, npm

### Local Development
```bash
# Clone repository
git clone https://github.com/SanaAdeelKhan/FailSim-AI.git
cd FailSim-AI

# Setup Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Add Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env

# Run backend
python src/main.py
# Backend runs on http://localhost:8000

# In new terminal: Run simulations
cd ../simulation
source ../venv/bin/activate
pip install pybullet numpy
python run_batch.py 50

# In new terminal: Analyze with AI
cd ..
source venv/bin/activate
python ai/analysis/analyze_real.py

# In new terminal: Run dashboard
cd frontend
npm install
npm run dev
# Dashboard opens at http://localhost:5173
```

---

## 📊 Live Demo

**🌐 Public Dashboard:** http://80.240.20.49  
**🔌 Backend API:** http://80.240.20.49:8000  

**Try it:**
```bash
# Get current stats
curl http://80.240.20.49:8000/api/stats

# Get AI insights
curl http://80.240.20.49:8000/api/insights
```

---

## 🎯 Key Features

### ✅ Real Physics
- Kuka iiwa7 specifications (100N gripper, 7kg payload)
- Actual physics equations: `F_grip = (m × g + m × a) / μ`
- No arbitrary probabilities - failures determined by physics

### ✅ Gemini AI Integration
- Analyzes failure patterns
- Explains physical mechanisms
- Generates actionable recommendations

### ✅ Production-Ready
- REST API for integration
- Scalable batch processing
- Web dashboard for visualization

### ✅ Hackathon Compliant
- Track 2: Simulation-to-Real Training & Evaluation
- Vultr VM backend (mandatory)
- Public web application
- Gemini AI for reasoning
- Software-only, simulation-first

---

## 👥 Team

Built by a distributed team for **Launch & Fund Hackathon**:

- **Sana Adeel Khan** - AI Architecture & Product Lead
- **Ahmed Gul** - Backend & Vultr Infrastructure  
- **Wajiha** - Simulation & Physics Engineering
- **Muqadas** - Frontend & Dashboard
- **Tooba** - Documentation & QA

---

## 🎯 Target Users

- **Robotics Startups:** Reduce hardware testing costs
- **Autonomous Systems Teams:** Discover edge cases early
- **QA Engineers:** Systematic failure analysis
- **Research Labs:** Validate before real-world deployment

---

## 💼 Business Value

**ROI Example:**
- **Traditional QA:** 2 weeks manual testing, $10K cost, 50 scenarios
- **FailSim AI:** 1 day automated testing, $0 marginal cost, 1000+ scenarios
- **Result:** 10x faster, 90% cost reduction, better coverage

---

## 📝 Documentation

- [Setup Guide](docs/setup/SETUP.md)
- [Architecture](docs/architecture.md)
- [API Documentation](http://80.240.20.49:8000/docs)

---

## 🏆 Hackathon

**Event:** Launch & Fund - AI Meets Robotics  
**Track:** Track 2 - Simulation-to-Real Training & Evaluation  
**Dates:** February 6-14, 2026  
**Organizer:** lablab.ai  

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 🙏 Acknowledgments

- **Vultr** - Cloud infrastructure partner
- **Google** - Gemini AI API access
- **PyBullet** - Physics simulation engine
- **lablab.ai** - Hackathon platform

---

**FailSim AI** — Because finding failures early is the fastest way to ship reliable robots. 🚀

*Built with ❤️ by Team FailSim*
