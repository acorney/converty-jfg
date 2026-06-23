@echo off
echo [Converty] Setting up Python environment...

python -m venv .venv
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

echo.
echo [Converty] Setup complete. Run launch.bat to start the app.
pause
