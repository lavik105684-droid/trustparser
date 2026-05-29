# SHARED TEAM MEMORY: Pixel Office Orchestrator

This document serves as the global context repository, project ledger, and operational policy protocol for the entire Core team.

---

## 🎯 Project Mission
Design and deploy a custom, highly optimized, lightweight automation engine and task scheduler managed through a beautiful 2D retro-styled visual desk dashboard (the **Pixel Office** concept).

---

## 🎨 Visual Design Reference & Mockup Spec
The design team (led by Daria, UI/UX) is developing our front-end panel based on this state-of-the-art pixel-art dashboard mock-up:

![Pixel Office Dashboard Mockup](C:\Users\lavik\.gemini\antigravity\brain\4b2333aa-7ee4-4292-bb8d-d76aaab77e33\pixel_office_dashboard_reference_1779551195109.png)

### Design Directives for the Swarm:
1. **Interactive Workstations:** Each agent is allocated an explicit desk mapped dynamically to its active state (Green: Active, Orange: Idle, Red: Blocked).
2. **Cozy Retro Vibe:** Employs detailed 2D isometric elements, wood flooring trims, indoor tropical potted plants, and glowing neon status boards.
3. **Split-Screen Terminal Console:** The right sidebar integrates a high-contrast monospaced log stream, styled with terminal command parameters.
4. **Legible Typography:** Employs sharp, clean borders and retro Outfit/Press-Start fonts to guarantee perfect readability.

---

## 🛡️ Gemini Token Budget Control Protocol (Критический лимит)

To ensure high cost-efficiency and prevent sudden API billing cutoffs or budget overruns, we enforce the **Token Budget Control Protocol**:

1. **Active Telemetry Monitoring:** The orchestrator tracks token expenditures (prompt and completion tokens) on every API request.
2. **The 20% Budget Threshold:** 
   - If the remaining Gemini API monthly/daily quota approaches **20% or less**, the system enters an **EMERGENCY PAUSE** state.
   - All background cron schedules, automated content scrapers, and AI generation tasks are immediately put on pause.
3. **Halt Condition:** The system logs `[EMERGENCY PAUSE] Gemini Token Quota reached remaining 20% margin` in `team_log.md` and displays a red warning bulb at all desks on the React visual dashboard.
4. **Resumption Condition:** Operations can only resume after a manual billing update or when the daily/monthly quota cycle resets.

---

## 📊 Next Sprint Milestones

- **Sprint 1 (Active):** Complete full React compilation and test FastAPI endpoints.
- **Sprint 2:** Build the custom node runner (implementing Python command executors and local Ollama routing).
- **Sprint 3:** Live integration of webhooks and automated Telegram CPA posting engines.
