# FailSim AI

**Automatic Failure Discovery & Root-Cause Analysis for Robotics — Before Hardware Exists**

[![Demo](https://img.shields.io/badge/Demo-Live-success)](YOUR_DEMO_URL)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🚨 The Problem

Most robotics development focuses on training policies and running limited tests before deploying to hardware. This approach hides critical risks:

- Rare but catastrophic failures
- Environment-specific brittleness  
- Unexplained performance drops during deployment

Real robotics teams pay heavily for late-stage failures, yet there are very few tools dedicated to **failure discovery** and **root-cause analysis** in simulation.

---

## 💡 Our Solution

**FailSim AI** is a simulation-first platform that automatically stress-tests robotic behaviors across thousands of scenarios and uses AI to explain why failures occur.

### What It Does

1. **Large-Scale Simulation**
   - Runs batch simulations of pick & place tasks
   - Applies domain randomization (friction, lighting, object weight)
   - Fully asynchronous and scalable

2. **Automatic Failure Discovery**
   - Collects telemetry and logs from every run
   - Detects task failures, partial successes, and performance degradation
   - Groups failures into meaningful clusters

3. **AI-Powered Root Cause Analysis**
   - Uses **Gemini Pro** to analyze structured metrics + logs
   - Generates human-readable explanations
   - Recommends actionable mitigation strategies

**Example Insight:**
> "The robot fails in 23% of runs when object weight exceeds 0.8kg on low-friction surfaces (μ < 0.3). Failures are caused by insufficient gripper hold force during placement motion, leading to premature object release."

---

## 🏗️ Architecture
```
[Simulation] → [Vultr Backend] → [Gemini Pro] → [Web Dashboard]
              ↓
         [Stores logs & metrics]
```

- **Simulation Layer:** Domain-randomized pick & place environment
- **Backend (Vultr VM):** Central orchestration, metrics storage, API endpoints
- **AI Layer:** Gemini Pro for failure clustering and root-cause reasoning
- **Frontend:** Interactive dashboard showing success rates, failure patterns, and AI insights

---

## ✅ Hackathon Compliance

✅ Track 2: Simulation-to-Real Training & Evaluation  
✅ Simulation-first, software-only robotics  
✅ Vultr VM backend as central data layer  
✅ Public web application  
✅ Gemini Pro for meaningful AI reasoning  
✅ Recorded demo video  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Vultr account

### Setup
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/FailSim-AI.git
cd FailSim-AI

# Backend setup
cd backend
pip install -r requirements.txt
python src/main.py

# Frontend setup
cd ../frontend
npm install
npm run dev

# Run simulation
cd ../simulation
python run_batch.py
```

See [docs/setup](./docs/setup/) for detailed instructions.

---

## 👥 Team

- **Sana** - AI Architecture & Product Lead
- **Ahmed Gul** - Backend & Vultr Infrastructure
- **Wajiha** - Simulation & Evaluation Engineering
- **Muqadas** - Frontend & Dashboard
- **Tooba** - Documentation & QA

---

## 🎯 Target Users

- Robotics startups
- Autonomous systems teams
- Robotics QA & validation engineers
- Research groups preparing for real-world deployment

---

## 📽️ Demo

🌐 **Live Demo:** [YOUR_URL_HERE]  
🎥 **Video Demo:** [TWITTER_LINK_HERE]

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🏆 Built for Launch & Fund Hackathon

**Track 2:** AI Meets Robotics - Simulation to Real  
**Event:** [Launch & Fund Hackathon](https://lablab.ai/ai-hackathons/launch-fund-ai-meets-robotics)

---

**FailSim AI** — because finding failures early is the fastest way to ship reliable robots.
