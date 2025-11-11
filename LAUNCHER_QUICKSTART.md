# Quick Start - NFL Betting System Launcher

## 30-Second Setup

### Step 1: Install Dependencies
```bash
cd C:\Users\scott\Desktop\nfl-betting-systemv2
python -m pip install pyperclip
```

Or just run the launcher - it will auto-install on first run.

### Step 2: Run the Launcher
```bash
python launcher.py
```

**OR** double-click `run_launcher.bat`

### Step 3: Use It

1. Select "Generate Parlays" or "View Top 20 Props"
2. Pick a week (e.g., Week 9)
3. Enter bankroll ($100)
4. Click "Run Analysis"
5. Wait for results preview
6. Results auto-copy to clipboard
7. Paste wherever you need them

---

## One-Time Setup for Desktop Shortcut

1. Right-click on `run_launcher.bat`
2. Click "Send to" → "Desktop (create shortcut)"
3. Now you can double-click the shortcut from desktop to launch

---

## Important: File Structure

Make sure you have CSV files in `nfl-betting-systemv2/data/` like:
- `wk8_offensive_DVOA.csv`
- `wk8_defensive_DVOA.csv`
- `wk8_betting_lines_draftkings.csv`
- `wk8-injury-report.csv` (note the HYPHEN)

If files are missing when you run, the launcher will tell you exactly what's needed.

---

## That's It!

No more terminal commands. Just:
1. Download/prepare data files
2. Double-click launcher shortcut
3. Select options
4. Copy results to clipboard

Questions? See LAUNCHER_README.md for full documentation.
