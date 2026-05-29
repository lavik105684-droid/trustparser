# IMPLEMENTATION PLAN: "Pixel Office" Agentic Orchestrator

This plan outlines the architecture, technology stack, folder structure, and deployment steps for our custom lightweight automation engine and React visual dashboard.

---

## 1. Technology Stack (Технологический стек)

### A. Frontend: Visual Retro Dashboard
- **Core Framework:** React 18+ (Vite for fast, modern edge compilation).
- **Styling & Theme:** TailwindCSS with a custom retro pixel font (e.g., `Press Start 2P` from Google Fonts). Custom 2D grid canvas or pixel-styled components.
- **Animations:** Framer Motion for dynamic desk overlays (agent activity bulbs, transition sweeps when status jumps from "idle" to "processing").
- **State Management:** React Context API or Zustand (for lightweight telemetry updates).

### B. Backend: Lightweight Orchestrator
- **Core Framework:** FastAPI (Python 3.10+) for fast async event processing.
- **Task Runner:** Custom background thread manager that reads `_core/shared_memory/workflow_state.json`, assigns tasks, and runs execution processes.
- **Local Inference Client:** Built-in Ollama REST API client (using `urllib` or `httpx` to trigger Llama 3.1/3.3).
- **Storage:** Local JSON files acting as zero-overhead context repositories (Shared Memory).

---

## 2. Directory Tree Structure (Структура папок)

```text
C:\Users\lavik\Documents\antigravity\modest-carson\
├── _core/
│   ├── agents/                     # Agent profile definitions
│   │   ├── lead_developer.md
│   │   ├── ui_ux_designer.md
│   │   ├── qa_engineer.md
│   │   ├── review_manager.md
│   │   └── growth_marketing_lead.md
│   ├── shared_memory/              # Shared data & state
│   │   ├── workflow_state.json
│   │   └── context_maps.json
│   ├── logs/                       # Agent communication ledgers
│   │   └── team_log.md
│   ├── backend/                    # FastAPI task orchestrator
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py             # FastAPI entrypoint & webhook endpoints
│   │   │   ├── scheduler.py        # Background task queue & thread pool
│   │   │   ├── agent_runner.py     # Local Ollama & cloud API interface
│   │   │   └── schemas.py          # JSON validation & Pydantic models
│   │   ├── requirements.txt
│   │   └── run.bat                 # Script to launch backend server
│   └── frontend/                   # React/Tailwind visual panel
│       ├── public/
│       │   └── pixel_assets/       # Retro visual components and icons
│       ├── src/
│       │   ├── components/
│       │   │   ├── AgentDesk.jsx   # Desk UI component (state, logs, bars)
│       │   │   ├── OfficeGrid.jsx  # Main canvas container
│       │   │   └── Terminal.jsx    # Real-time logging console
│       │   ├── App.jsx
│       │   ├── index.css
│       │   └── main.jsx
│       ├── tailwind.config.js
│       ├── vite.config.js
│       └── package.json
```

---

## 3. "Pixel Office" Grid Layout Concept

The interface is structured as an interactive 2D overhead retro office layout matching the visual reference:

```
+--------------------------------------------------------------+
| [PIXEL OFFICE DASHBOARD]                     [Status: STABLE] |
+--------------------------------------------------------------+
|                                                              |
|   +-------------------+              +-------------------+   |
|   | [DESK 1: Leo]     |              | [DESK 2: Daria]   |   |
|   | Role: Developer   |              | Role: UI Designer |   |
|   | Task: Setup API   |              | Task: Draw Assets |   |
|   | Status: [ACTIVE]  |              | Status: [IDLE]    |   |
|   +-------------------+              +-------------------+   |
|                                                              |
|   +-------------------+              +-------------------+   |
|   | [DESK 3: Quentin] |              | [DESK 4: Regina]  |   |
|   | Role: QA Engineer |              | Role: Review Mgr  |   |
|   | Task: Setup Tests |              | Task: Lint Code   |   |
|   | Status: [ACTIVE]  |              | Status: [ACTIVE]  |   |
|   +-------------------+              +-------------------+   |
|                                                              |
|                  +-------------------+                       |
|                  | [DESK 5: Gary]    |                       |
|                  | Role: Marketing   |                       |
|                  | Task: Keyword SEO |                       |
|                  | Status: [IDLE]    |                       |
|                  +-------------------+                       |
|                                                              |
+--------------------------------------------------------------+
| > Console: [2026-05-23T17:25] Quentin pushed standard tests  |
+--------------------------------------------------------------+
```

### Visual Desk UI Logic
- **Activity Status Bulb:** Soft pulsing color dot (Green: Processing, Blue: Idle, Red: Error/OOM blocked).
- **Progress Bar:** Retro retro pixel bar mapping the agent's current task completion percentage.
- **Terminal Console:** Streams direct outputs from `_core/logs/team_log.md` in real-time.
