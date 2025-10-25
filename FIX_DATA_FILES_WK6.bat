@echo off
echo ============================================================
echo FIXING DATA FILE NAMES FOR WEEK 6
echo ============================================================
echo.

cd C:\Users\scott\Desktop\nfl-betting-system\data

echo Files already exist for Week 6 DVOA!
echo Just need to create a Week 6 projection file...

echo.
echo Creating Week 6 projection from Week 8 data...
copy "NFL_Projections___Wk_8_updated.csv" "NFL_Projections_Wk_6_updated.csv"

echo.
echo ============================================================
echo DONE! Files ready for Week 6
echo ============================================================
echo.
echo Next step: Update .env file
echo   Change: NFL_WEEK=7
echo   To:     NFL_WEEK=6
echo.
echo Note: Using Week 8 projections for Week 6
echo This is fine for testing!
echo.
pause
