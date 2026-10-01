@echo off
echo ========================================
echo  BIS Sahayak - Backend Server Starting
echo ========================================
cd /d "%~dp0"
echo Starting FastAPI backend on http://localhost:8000 ...
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
pause
