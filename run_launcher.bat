@echo off
REM NFL Betting System Launcher Batch File
REM Run from desktop or anywhere

cd /d "%~dp0"

REM Check if pyperclip is installed
python -c "import pyperclip" 2>nul
if errorlevel 1 (
    echo Installing required dependencies...
    python -m pip install -q -r launcher_requirements.txt
)

REM Run the launcher
python launcher.py

pause
