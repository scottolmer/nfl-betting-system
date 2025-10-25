@echo off
echo ============================================================
echo NFL BETTING SYSTEM - STARTUP LAUNCHER
echo ============================================================
echo.
echo Starting all components...
echo.
echo This will open 3 terminal windows:
echo   1. Enhanced Slack Bot
echo   2. Line Monitor with Confidence
echo   3. Instructions for ngrok
echo.
pause
echo.

cd /d C:\Users\scott\Desktop\nfl-betting-system

echo Starting Terminal 1: Enhanced Slack Bot...
start cmd /k "title SLACK BOT (Enhanced) && python scripts\slack_bot\app_enhanced.py"

timeout /t 3

echo Starting Terminal 2: Enhanced Line Monitor...
start cmd /k "title LINE MONITOR (Enhanced) && python scripts\line_monitoring\monitor_enhanced.py"

timeout /t 2

echo Starting Terminal 3: ngrok Instructions...
start cmd /k "title NGROK TUNNEL && echo. && echo ============================================ && echo NGROK TUNNEL && echo ============================================ && echo. && echo Run this command: && echo    ngrok http 3000 && echo. && echo Then: && echo   1. Copy the forwarding URL && echo   2. Update Slack app settings && echo   3. Test with /betting_help && echo. && echo ============================================ && echo."

echo.
echo ============================================================
echo All terminals launched!
echo ============================================================
echo.
echo Next steps:
echo   1. In Terminal 3, run: ngrok http 3000
echo   2. Copy the forwarding URL to Slack app settings
echo   3. Test in Slack: /betting_help
echo.
echo Press any key to exit this window...
pause > nul
