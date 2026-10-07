@echo off
setlocal EnableExtensions
cd /d "%~dp0.."
title JARVIS - BUILT BY DILIP - Windows Setup
where py >nul 2>&1
if errorlevel 1 (
 echo Python 3.10+ was not found. Install Python for Windows 10/11.
 echo Windows 7/8 are legacy targets and may require a compatible backend.
 pause
 exit /b 1
)
py -3.10 -m venv .venv >nul 2>&1
if errorlevel 1 py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -e ".[airllm,test]"
if errorlevel 1 (
 echo AirLLM install failed; installing the lightweight core.
 .venv\Scripts\python.exe -m pip install -e ".[test]"
)
echo Installation complete.
echo Run scripts\RUN_JARVIS.bat
pause
