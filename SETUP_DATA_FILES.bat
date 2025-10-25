@echo off
echo ============================================================
echo SETTING UP DATA FILES - COMPLETE FIX
echo ============================================================
echo.
echo This will:
echo   1. Copy all files from project to data folder
echo   2. Rename betting lines to correct format
echo   3. Set up for Week 7
echo.
pause
echo.

cd C:\Users\scott\Desktop\nfl-betting-system

echo Creating data folder if needed...
if not exist "data" mkdir data

echo.
echo Copying DVOA files for Week 6...
copy "DVOA_Off_wk_6.csv" "data\DVOA_Off_wk_6.csv"
copy "DVOA_Def_wk_6.csv" "data\DVOA_Def_wk_6.csv"
copy "Def_vs_WR_wk_6.csv" "data\Def_vs_WR_wk_6.csv"

echo.
echo Copying betting lines for Week 7...
copy "Betting_Lines_wk_7_Saturday__Sheet1.csv" "data\betting_lines_wk_7.csv"

echo.
echo Copying injury report...
copy "week7_injury_report.txt" "data\week7_injury_report.txt"

echo.
echo Creating Week 7 DVOA files (using Week 6 data - most recent)...
copy "data\DVOA_Off_wk_6.csv" "data\DVOA_Off_wk_7.csv"
copy "data\DVOA_Def_wk_6.csv" "data\DVOA_Def_wk_7.csv"
copy "data\Def_vs_WR_wk_6.csv" "data\Def_vs_WR_wk_7.csv"

echo.
echo ============================================================
echo DONE! All data files ready for Week 7
echo ============================================================
echo.
echo Files created:
echo   - DVOA_Off_wk_7.csv
echo   - DVOA_Def_wk_7.csv
echo   - Def_vs_WR_wk_7.csv
echo   - betting_lines_wk_7.csv
echo   - week7_injury_report.txt
echo.
echo Your .env is already set to NFL_WEEK=7 ✓
echo.
echo Next: Run TEST_SYSTEM.bat to verify
echo.
pause
