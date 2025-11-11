@echo off
REM NFL Betting System - Streamlit UI Launcher
REM Run this from the project root directory

echo.
echo ========================================
echo   NFL Betting System - Streamlit UI
echo ========================================
echo.

REM Check if python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if streamlit is installed
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Installing Streamlit and dependencies...
    cd ui
    pip install -r requirements.txt
    cd ..
)

REM Check if .env exists
if not exist .env (
    echo WARNING: .env file not found
    echo Please create .env with ANTHROPIC_API_KEY before running
    echo Example:
    echo   ANTHROPIC_API_KEY=sk-ant-...
    echo.
)

REM Launch Streamlit
echo Starting NFL Betting System Dashboard...
echo.
echo The dashboard will open in your browser at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

python -m streamlit run ui/app.py

pause
