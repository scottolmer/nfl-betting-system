@echo off
REM NFL Betting System - Windows Setup Script

echo.
echo ========================================
echo    NFL BETTING SYSTEM - WINDOWS SETUP
echo ========================================
echo.

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

echo Generating code files...
echo.

python generate_code.py

echo.
echo ========================================
echo    SETUP COMPLETE!
echo ========================================
echo.
echo NEXT STEPS:
echo.
echo 1. Copy .env.example to .env:
echo    copy .env.example .env
echo.
echo 2. Edit .env and add your API keys:
echo    notepad .env
echo.
echo 3. Test the system:
echo    python scripts\core\main.py
echo.
echo 4. Read START_HERE.md for full instructions
echo.
pause
