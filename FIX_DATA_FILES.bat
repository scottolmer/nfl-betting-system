@echo off
echo ============================================================
echo FIXING DATA FILE NAMES FOR WEEK 8
echo ============================================================
echo.

cd C:\Users\scott\Desktop\nfl-betting-system\data

echo Copying Week 6 DVOA files to Week 8...
copy DVOA_Off_wk_6.csv DVOA_Off_wk_8.csv
copy DVOA_Def_wk_6.csv DVOA_Def_wk_8.csv
copy Def_vs_WR_wk_6.csv Def_vs_WR_wk_8.csv

echo.
echo Fixing projection filename (triple underscore to single)...
copy "NFL_Projections___Wk_8_updated.csv" "NFL_Projections_Wk_8_updated.csv"

echo.
echo ============================================================
echo DONE! Files ready for Week 8
echo ============================================================
echo.
echo Next step: Update .env file
echo   Change: NFL_WEEK=7
echo   To:     NFL_WEEK=8
echo.
pause
