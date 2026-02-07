# FailSim AI - Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- Vultr account
- Google AI API key (Gemini Pro)

---

## Backend Setup (Ahmed)
```bash
cd backend
pip install -r requirements.txt

# Set environment variables
export VULTR_API_KEY="your_key"
export GEMINI_API_KEY="your_key"

# Run backend
python src/main.py
```

Backend will run on `http://localhost:8000`

---

## Simulation Setup (Wajiha)
```bash
cd simulation
pip install -r requirements.txt

# Run batch simulation
python run_batch.py --runs 100
```

Outputs saved to `simulation/outputs/`

---

## Frontend Setup (Muqadas)
```bash
cd frontend
npm install

# Set backend URL
echo "VITE_API_URL=http://localhost:8000" > .env

# Run frontend
npm run dev
```

Frontend will run on `http://localhost:5173`

---

## Testing
```bash
# Test backend API
curl http://localhost:8000/health

# Test simulation
python simulation/test_single_run.py
```

---

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for Vultr deployment instructions.
