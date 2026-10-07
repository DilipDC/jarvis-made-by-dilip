@echo off
setlocal
cd /d "%~dp0.."
if not exist .venv\Scripts\python.exe call scripts\install_windows.bat
if not exist .venv\Scripts\python.exe exit /b 1
start "JARVIS Server" /min .venv\Scripts\python.exe -m uvicorn jarvis_app.core.app:app --host 127.0.0.1 --port 8000
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:8000
