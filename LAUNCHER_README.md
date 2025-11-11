# NFL Betting System Launcher

A desktop GUI launcher for the NFL Betting System that eliminates the need for terminal commands.

## Features

✅ **Generate Parlays** - Runs both traditional and enhanced (low-correlation) parlays simultaneously  
✅ **View Top 20 Props** - Displays ranked player props for the week  
✅ **File Validation** - Checks for required data files before running  
✅ **Real-time Progress** - Shows analysis progress with visual indicators  
✅ **Results Preview** - Resizable window to review results before copying  
✅ **Auto-copy** - Automatically copies results to clipboard  
✅ **Multiple Runs** - Run back-to-back analyses without closing the app  

## Setup

### 1. Install Dependencies (First Time Only)

```bash
cd C:\Users\scott\Desktop\nfl-betting-systemv2
python -m pip install pyperclip
```

Or just run the launcher - it will auto-install on first run.

### 2. Create Desktop Shortcut (Optional)

**Windows:**
- Right-click `run_launcher.bat` → Send to → Desktop (create shortcut)
- Double-click the shortcut to launch

## Usage

1. **Run the Launcher**
   ```bash
   python launcher.py
   ```
   
   Or double-click `run_launcher.bat`

2. **Select Action**
   - Generate Parlays (Traditional + Enhanced)
   - View Top 20 Props

3. **Select Week**
   - Dropdown shows weeks 1-17
   - **Important:** System analyzes the PREVIOUS week
   - Example: Select "Week 9" → analyzes "Week 8"

4. **Enter Bankroll** (Required)
   - Enter your betting bankroll (e.g., $100)
   - Displayed at $10/unit in results

5. **Click "Run Analysis"**
   - System validates data files
   - Progress window shows real-time updates
   - Results display in preview window

6. **Review & Copy**
   - Results automatically copied to clipboard
   - Preview window shows markdown format
   - Paste into Notes, Docs, or wherever you need it

## File Requirements

### Required Files (Analysis won't run without these)
```
wkX_offensive_DVOA.csv          (offensive DVOA ratings)
wkX_defensive_DVOA.csv          (defensive DVOA ratings)
wkX_betting_lines_draftkings.csv (DraftKings betting lines)
wkX-injury-report.csv           (injury reports - NOTE: uses hyphen, not underscore)
```

### Optional Files (Analysis continues if missing, shows warning)
```
wkX_passing_base.csv            (passing statistics)
wkX_receiving_base.csv          (receiving statistics)
wkX_rushing_base.csv            (rushing statistics)
wkX_def_v_wr_DVOA.csv           (defensive vs WR matchups)
wkX_receiving_alignment.csv     (receiving alignment)
wkX_receiving_usage.csv         (receiving usage)
```

**Note:** All files go in `data/` folder (not in subfolders)

## File Naming Important Notes

- **Week Format:** `wkX` where X is the week number (e.g., `wk8`, `wk9`, `wk10`)
- **Capitalization:** Must match exactly (e.g., `DVOA` in caps)
- **Injuries File:** Uses HYPHEN `wk8-injury-report.csv` NOT underscore
- **Location:** Root `data` folder, not in subfolders
- **Common Issues:**
  - Files in nested folders won't be found
  - Typos in filenames (dvoa vs DVOA)
  - Using underscore in injury filename instead of hyphen

If files are missing, the error message will show you exactly what it's looking for.

## Output Formats

### Parlay Generation Output
Shows both traditional parlays and enhanced (low-correlation) parlays side-by-side:
- Parlay type (2-leg, 3-leg, 4-leg, 5-leg)
- Confidence percentage
- Bet size in units (and $ at $10/unit)
- Individual legs (player, stat, over/under, line)

### Top Props Output
Ranked list of top 20 props:
- Player name and team
- Stat type and line
- Confidence percentage
- Opponent

## Troubleshooting

### "Missing Required Files"
1. Check that files are in `nfl-betting-systemv2/data/` folder
2. Verify filenames match the pattern exactly
3. Check spelling and capitalization
4. Make sure `wk-injury-report.csv` uses a HYPHEN, not underscore

### "Analysis failed"
1. Check that `.env` file exists and has `ANTHROPIC_API_KEY` set
2. Verify internet connection (for API calls)
3. Check that ports are available (no other processes using them)

### Results not copying to clipboard
- Try clicking "Copy to Clipboard" button in preview window manually

### Slow analysis
- This is normal - DVOA analysis and Claude dependency analysis can take 30-60 seconds
- Progress window shows what's happening
- Can't cancel mid-analysis, but can close window after it completes

## Advanced Usage

### Command Line (for scripting)
```bash
python launcher.py  # GUI mode
```

Or use `run.py` directly for scripting:
```bash
python run build-parlays-optimized 8
python run analyze week 8
```

## Tips

- Always verify data files are in place BEFORE running analysis
- Start with week 2+ to ensure previous week has data
- Bankroll value doesn't affect analysis - just used for display
- Results are automatically saved to `parlay_runs/` folder
- Can run multiple analyses back-to-back without restarting launcher

## Support

For issues or questions, check the main project README.md or look at parlay_runs folder for previous results.
