# FailSim AI - System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     FailSim AI Architecture                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   SIMULATION     │  (Wajiha)
│   Pick & Place   │
│   Robot Task     │
│                  │
│ • Object weight  │
│ • Friction       │
│ • Lighting       │
└────────┬─────────┘
         │
         │ Logs + Metrics (JSON)
         ▼
┌──────────────────┐
│  VULTR BACKEND   │  (Ahmed) ⭐ MANDATORY
│                  │
│ • Job queue      │
│ • Metrics DB     │
│ • REST API       │
└────────┬─────────┘
         │
         │ Fetch failure data
         ▼
┌──────────────────┐
│   GEMINI PRO     │  (Sana)
│   AI Analysis    │
│                  │
│ • Cluster fails  │
│ • Explain cause  │
│ • Suggest fixes  │
└────────┬─────────┘
         │
         │ AI Insights (JSON + Text)
         ▼
┌──────────────────┐
│  WEB DASHBOARD   │  (Muqadas)
│                  │
│ • Success rate   │
│ • Failure charts │
│ • AI explanations│
└──────────────────┘
```

## Data Flow

1. **Simulation → Backend**
   - Wajiha's simulation outputs JSON logs per run
   - Backend stores in database

2. **Backend → Gemini**
   - Backend batches failed runs
   - Sends to Gemini for analysis

3. **Gemini → Backend**
   - Returns clustered failures + explanations
   - Backend stores AI insights

4. **Backend → Frontend**
   - REST API serves data
   - Dashboard visualizes results

## Technology Stack

- **Simulation:** Python (PyBullet / MuJoCo)
- **Backend:** Python (FastAPI) on Vultr VM
- **AI:** Google Gemini Pro API
- **Frontend:** React + Tailwind CSS
- **Database:** PostgreSQL / SQLite
