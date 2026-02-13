# FailSim AI ⚡
**Multi-Robot Failure Discovery & Root-Cause Analysis Platform**

[![Live Demo](https://img.shields.io/badge/Live-Demo-success)](http://80.240.20.49) [![Backend](https://img.shields.io/badge/API-Running-blue)](http://80.240.20.49:8000) [![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🚨 The Problem

Robotics companies generate massive simulation data but struggle to understand:
- **Which combinations cause failures?**
- **What are the root physical causes?**
- **How to prioritize fixes?**

**Traditional approach:**
- ❌ Manual log review by engineers
- ❌ Slow, expensive, error-prone
- ❌ Misses subtle patterns

**FailSim AI approach:**
- ✅ Automated physics-based testing
- ✅ AI-powered root cause analysis with Gemini 3 Flash
- ✅ Multi-robot support (Kuka, Franka Panda, UR5, + Custom)
- ✅ Real-time visualization & charts

---

## 💡 Our Solution

**FailSim AI** is a physics-based simulation platform that automatically discovers failure patterns across multiple robot types and uses **Gemini 3 Flash AI** to explain WHY robots fail.

### Real-World Use Case
**Company:** Warehouse automation startup  
**Robot:** Kuka iiwa7 collaborative arm  
**Challenge:** Pick & place fails unpredictably in production  

**Before FailSim AI:**
> "Our robot fails sometimes. Let's manually test 100 combinations and guess why."  
> **Cost:** 2 weeks, $10K in engineer time

**With FailSim AI:**
> "Run 1000 simulations overnight. FailSim AI reports: 'Failures occur when required grip force exceeds 100N (weight > 1.1kg AND friction < 0.32). Recommendation: Increase gripper force by 15%'"  
> **Cost:** 1 day, automated

---

## 🤖 What FailSim AI Does

### 1. **Multi-Robot Physics Simulation**
- **3 Built-in Robots:**
  - Kuka iiwa7 (100N force, 7kg payload)
  - Franka Emika Panda (70N force, 3kg payload)
  - Universal Robots UR5 (150N force, 5kg payload)
- **Custom Robot Support:** Users can define their own robot specs
- **Real Physics:** PyBullet 3D engine with actual equations
- **Domain Randomization:** Weight, friction, lighting variance

### 2. **Automatic Failure Discovery**
- Runs 100s of simulations
- Physics-driven failures (not random):
  - Gripper force insufficient
  - Object slips during acceleration
  - Vision errors from poor lighting

### 3. **AI-Powered Analysis (Gemini 3 Flash)**
- Analyzes failure clusters
- Generates human-readable explanations
- Provides engineering recommendations
- Fallback to Gemini 2.5 Flash if quota exceeded

### 4. **Interactive Features**
- **Experiment Runner:** Configure and run simulations from dashboard
- **Live Visualization:** See 5 key frames of robot simulation
- **Click-to-Analyze:** Get AI analysis for individual runs
- **Failure Charts:** Weight/friction distribution visualizations
- **Custom Robots:** Add your own robot specifications

---

## 🏗️ Architecture
```
┌─────────────────┐
│   PyBullet      │  Multi-Robot Physics Simulation
│   3 Robots      │  • Kuka iiwa7, Franka, UR5
│   + Custom      │  • Real physics equations
└────────┬────────┘
         │ Simulation Results (JSON)
         ▼
┌─────────────────┐
│  Vultr Backend  │  Central System of Record
│  FastAPI        │  • REST API (Port 8000)
│  Frankfurt VM   │  • Experiment orchestration
└────────┬────────┘
         │ Failure Data
         ▼
┌─────────────────┐
│  Gemini 3 Flash │  AI Analysis
│  (+ 2.5 fallback)│  • Root cause analysis
│                 │  • Physics explanations
└────────┬────────┘
         │ AI Insights
         ▼
┌─────────────────┐
│  React          │  Interactive Dashboard
│  Dashboard      │  • Multi-robot selection
│  Port 80        │  • Live visualizations
└─────────────────┘
```

**Tech Stack:**
- **Simulation:** PyBullet, Python 3.10, NumPy
- **Backend:** FastAPI, Vultr VM (Frankfurt)
- **AI:** Google Gemini 3 Flash API (with 2.5 fallback)
- **Frontend:** React, Tailwind CSS, Vite
- **Deployment:** Nginx, Screen sessions

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
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Add Gemini API key
echo "GEMINI_API_KEY=your_key_here" > .env

# Run backend
python src/main.py
# Backend: http://localhost:8000

# New terminal: Run frontend
cd ../frontend
npm install
npm run dev
# Dashboard: http://localhost:5173
```

---

## 📊 Live Demo

🌐 **Dashboard:** http://80.240.20.49  
🔌 **API Docs:** http://80.240.20.49:8000/docs

### Try it:
```bash
# Get stats
curl http://80.240.20.49:8000/api/stats

# Get AI insights
curl http://80.240.20.49:8000/api/insights

# Get available robots
curl http://80.240.20.49:8000/api/robots
```

---

## 🎯 Key Features

### ✅ Multi-Robot Support
- 3 pre-configured industrial robots
- Custom robot creation with user-defined specs
- Different physics parameters per robot type

### ✅ Real Physics
- Actual robot specifications (gripper force, payload, acceleration)
- Physics equations: `F_grip = (m × g + m × a) / μ`
- No arbitrary probabilities

### ✅ Gemini 3 AI Integration
- Automatic fallback to Gemini 2.5 if quota exceeded
- Failure pattern analysis
- Physical mechanism explanations
- Actionable recommendations

### ✅ Interactive Dashboard
- **Experiment Runner:** Configure simulations (runs, robot type)
- **Live Visualization:** 5-frame robot simulation capture
- **Click-to-Analyze:** Individual run AI analysis
- **Charts:** Error distribution, weight/friction patterns
- **Custom Robots:** Add your own robot specs on-the-fly

### ✅ Production-Ready
- REST API for integration
- Scalable batch processing
- 24/7 deployment on Vultr
- Web dashboard with real-time updates

---

## 👥 Team

Built by **Team FailSim** for Launch & Fund Hackathon:

- **Sana Adeel** - AI Architecture & Full-Stack Development
- **Wajiha Saleem** - Simulation & Physics Engineering  
- **Tooba Muzaffar** - Frontend & UX Design
- **Ghulam Hussain Ali** - Backend Infrastructure
- **Muhammad Zargham Khan** - Documentation & Testing

---

## 🎯 Target Users

- **Robotics Startups:** Reduce hardware testing costs
- **Autonomous Systems Teams:** Discover edge cases early
- **QA Engineers:** Systematic failure analysis
- **Research Labs:** Validate before real-world deployment

---

## 💼 Business Value

**ROI Example:**

| Approach | Time | Cost | Scenarios |
|----------|------|------|-----------|
| **Traditional QA** | 2 weeks | $10K | 50 |
| **FailSim AI** | 1 day | ~$0 | 1000+ |
| **Result** | **10x faster** | **90% cheaper** | **20x coverage** |

---

## 🏆 Hackathon

**Event:** Launch & Fund - AI Meets Robotics  
**Track:** Track 2 - Simulation-to-Real Training & Evaluation  
**Dates:** February 6-14, 2026  
**Organizer:** lablab.ai  

### Compliance Checklist
- ✅ Track 2: Simulation-to-Real evaluation pipeline
- ✅ Vultr VM backend (mandatory)
- ✅ Public web application
- ✅ Gemini AI integration (3 Flash + 2.5 fallback)
- ✅ Software-only, simulation-first
- ✅ Production-ready web app
- ✅ GitHub repository with docs

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
