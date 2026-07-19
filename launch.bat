@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [Converty] No virtual environment found. Running setup first...
    call setup.bat
)

.venv\Scripts\pythonw.exe main.py
