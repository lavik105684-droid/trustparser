@echo off
title Pixel Office Swarm Orchestrator Launchpad
echo ===================================================
echo [STARTING] Launching Pixel Office Orchestrator...
echo ===================================================

echo [1/3] Starting FastAPI Backend on Port 8000...
start "FastAPI Backend" cmd /k "python main.py"

echo [2/3] Starting Vite Frontend on Port 5173...
cd _core\frontend
start "Vite Frontend" cmd /k "npm run dev"

echo [3/3] Synchronizing nodes... Waiting 5 seconds...
timeout /t 5 /nobreak > nul

echo [SUCCESS] Launching visual desk dashboard in browser...
start http://localhost:5173/
