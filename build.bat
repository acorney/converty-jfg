@echo off
cd /d "%~dp0"
echo [Converty] Building standalone .exe with PyInstaller...

call .venv\Scripts\activate.bat
pyinstaller converty.spec --clean --noconfirm

echo.
echo [Converty] Build complete. Executable is in dist\Converty\Converty.exe
pause
