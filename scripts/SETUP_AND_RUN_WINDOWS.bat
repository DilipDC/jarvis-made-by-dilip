@echo off
setlocal
cd /d "%~dp0.."
call scripts\install_windows.bat
if errorlevel 1 exit /b 1
call scripts\RUN_JARVIS.bat
