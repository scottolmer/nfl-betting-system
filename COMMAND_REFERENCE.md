# NFL Betting System - Command Reference Guide

Complete list of all commands you can run for your NFL betting analysis system.

---

## 📋 Table of Contents

1. [Core Analysis Commands](#core-analysis-commands)
2. [Data & Roster Management](#data--roster-management)
3. [Slack Bot & Monitoring](#slack-bot--monitoring)
4. [Betting & Tracking](#betting--tracking)
5. [Diagnostics & Debugging](#diagnostics--debugging)
6. [Weekly Workflow](#weekly-workflow)

---

## Core Analysis Commands

### Generate Parlays (Main Command)

**Basic - Skip fetching new odds (use cached data)**
```bash
python scripts/run_analysis.py --week 8 --skip-fetch
```

**With Fresh Odds - Fetch latest lines from The Odds API**
```bash
python scripts/run_analysis.py --week 8
```

**Different Week**
```bash
python scripts/run_analysis.py --week 9 --skip-fetch
```

**Output:** 
- Generates 10 optimized parlays
- Saves to `data/week8_betting_card.txt`
- Console output shows all parlay details with confidence scores

---

## Data & Roster Management

### Roster Diagnostics

**Check which players are missing from roster**
```bash
python quick_diagnostic.py
```

**Shows:**
- Missing players list
- How many props each player would contribute
- Current match rate (should be 96%+)

### Fix Specific Players

**Fix Marquise Brown team (WAS not ARI)**
```bash
python fix_marquise_brown.py
```

**General player fix template** (edit as needed)
```bash
python <script_name>.py
```

### Roster Generation

**Auto-generate enhanced roster from betting lines**
```bash
python build_enhanced_roster.py
```

**Output:** `data/NFL_roster_ENHANCED.csv`

### Identify Missing Players

**Find all players missing from roster**
```bash
python identify_missing_roster_players.py
```

**Shows:**
- Complete list of missing players
- Which games they appear in
- Recommended team assignments

---

## Slack Bot & Monitoring

### Start Slack Bot (Interactive Commands)

**Start the enhanced Slack bot**
```bash
python scripts/slack_bot/app_enhanced.py
```

**Slack Commands Available:**
- `/analyze_props` - Get top 10 analyzed props
- `/build_parlays` - Generate optimal parlays
- `/check_confidence` - Look up confidence for specific player
- `/line_movement` - Check recent line movements
- `/fetch_odds` - Manually pull latest odds
- `/system_status` - Health check on system

### Start Line Monitoring (Background)

**Monitor line movements and alert to Slack**
```bash
python scripts/line_monitoring/monitor_enhanced.py --week 8
```

**What it does:**
- Runs continuously
- Checks for line movements every 60 minutes
- Sends Slack alerts when steam detected
- Enriches alerts with system confidence scores

**Stop monitoring:** Press `CTRL+C`

### Main Monitoring Script

**Alternative monitoring approach**
```bash
python scripts/line_monitoring/monitor_main_enhanced.py --week 8
```

---

## Betting & Tracking

### Analyze Bet Results

**Generate calibration report on tracked parlays**
```bash
python scripts/analyze_parlay_bets.py
```

**Requires:**
- Updated `data/PARLAY_BET_TRACKER.csv` with results
- WON/LOST/PUSH columns filled in

**Output:**
- Hit rates by confidence tier
- ROI analysis
- Calibration recommendations

### Generate Betting Card

**Create formatted betting card from parlays**
```bash
python scripts/generate_betting_card.py
```

---

## Diagnostics & Debugging

### System Diagnostics

**Check environment and all API keys**
```bash
python diagnose_env.py
```

**Verifies:**
- Python version
- Required libraries installed
- API keys configured
- Data files present

### Verify Data Loader

**Test data loading pipeline**
```bash
python scripts/verify_loader.py
```

**Checks:**
- Roster file loads correctly
- DVOA files parse properly
- Betting lines transform successfully
- Props get assigned to teams

### Test System End-to-End

**Run full system test**
```bash
python test_system.py
```

**Tests:**
- All data loads
- All agents initialize
- Analysis runs
- Parlays build

### Check Player Names

**Debug player name matching issues**
```bash
python check_names.py
```

### Find Name Mismatches

**Compare roster vs betting lines names**
```bash
python find_name_mismatches.py
```

**Shows:**
- Which names don't match between files
- Normalization issues
- Formatting problems

### Clear Python Cache

**Clear all cached data (fixes stale data issues)**
```bash
python scripts/clear_all_cache.py
```

**Clears:**
- `__pycache__` directories
- Cached analysis results
- Stale prop data

### Debug Specific Issues

**Debug agent analysis**
```bash
python debug_agents.py
```

**Debug confidence scoring**
```bash
python debug_confidence.py
```

**Debug name matching**
```bash
python debug_names.py
```

**Debug team mapping**
```bash
python debug_teams.py
```

---

## Weekly Workflow

### Complete Sunday Workflow

```bash
# 1. Generate fresh parlays (Sunday morning/early afternoon)
python scripts/run_analysis.py --week 8 --skip-fetch

# 2. Review output in terminal and in:
#    data/week8_betting_card.txt

# 3. Place 10 parlays on your sportsbook

# 4. Log them in the tracker
#    Open: data/PARLAY_BET_TRACKER.csv
#    Add rows for each parlay placed

# 5. Start line monitoring (optional)
python scripts/line_monitoring/monitor_enhanced.py --week 8
```

### Friday End-of-Week Analysis

```bash
# 1. Update tracker with results
#    Open: data/PARLAY_BET_TRACKER.csv
#    Fill in: Date, Week, Legs, Stats, Lines, Confidence, Units, Result (WON/LOST/PUSH)

# 2. Generate calibration report
python scripts/analyze_parlay_bets.py

# 3. Review report to understand:
#    - Which confidence tiers are working
#    - Hit rates by leg count
#    - ROI by position diversity
#    - Recommendations for next week
```

---

## Setup & Installation Commands

### Initial Setup

**Install all dependencies**
```bash
pip install -r requirements.txt
```

**Minimal install (if you have conflicts)**
```bash
pip install -r requirements-minimal.txt
```

### Environment Setup

**Set up environment variables (.env file)**
```bash
# Create .env file with:
ODDS_API_KEY=your_api_key_here
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
NFL_WEEK=8
```

### Docker Setup (Optional)

**Build Docker image**
```bash
docker build -f docker/Dockerfile -t nfl-betting-system .
```

**Run in Docker**
```bash
docker-compose -f docker/docker-compose.yml up
```

---

## Utility Commands

### Check Prop Variety

**Verify position diversity in parlays**
```bash
python scripts/check_variety.py
```

### Transform Betting Data

**Transform raw betting CSV to standardized format**
```bash
python scripts/transform_betting_data.py
```

### Copy Uploaded Files

**Copy data files from uploads directory**
```bash
python scripts/copy_uploaded_files.py
```

### Test System for Week 7

**Run week 7 test (for comparison)**
```bash
python scripts/test_week7.py
```

**Fresh week 7 test**
```bash
python scripts/test_week7_fresh.py
```

### Analyze Aggregation

**Test stats aggregation logic**
```bash
python test_aggregation.py
```

---

## API & Data Fetching

### Fetch Latest Odds

**Get fresh odds from The Odds API**
```bash
python scripts/fetch_odds.py
```

**From within analysis:**
```bash
# Just omit --skip-fetch flag
python scripts/run_analysis.py --week 8
```

### Find Elite Props

**Find highest-confidence props**
```bash
python scripts/find_elite_props.py
```

---

## Common Scenarios

### Scenario 1: Regular Sunday Analysis

```bash
# Step 1: Generate parlays for the week
python scripts/run_analysis.py --week 8 --skip-fetch

# Step 2: Review the betting card
# (Read: data/week8_betting_card.txt)

# Step 3: Check if roster has all players (optional)
python quick_diagnostic.py

# Step 4: Place bets and log in tracker
# (Edit: data/PARLAY_BET_TRACKER.csv)

# Step 5: Monitor line movements (optional, run in separate terminal)
python scripts/line_monitoring/monitor_enhanced.py --week 8
```

### Scenario 2: Friday Calibration

```bash
# Update tracker with results first, then:
python scripts/analyze_parlay_bets.py

# Review output to calibrate for next week
```

### Scenario 3: Troubleshooting Missing Props

```bash
# Check what players are missing
python quick_diagnostic.py

# See exactly which ones
python find_name_mismatches.py

# Fix roster (choose one):
python build_enhanced_roster.py  # Auto-generate
# OR manually add players to: data/NFL_roster - Sheet1.csv

# Test the fix
python scripts/verify_loader.py

# Re-run analysis
python scripts/run_analysis.py --week 8 --skip-fetch
```

### Scenario 4: Debug Analysis Issues

```bash
# Test system loads correctly
python test_system.py

# Verify data loading
python scripts/verify_loader.py

# Check environment
python diagnose_env.py

# Clear cache and retry
python scripts/clear_all_cache.py
python scripts/run_analysis.py --week 8 --skip-fetch
```

### Scenario 5: Using Slack Bot

```bash
# Terminal 1: Start the bot
python scripts/slack_bot/app_enhanced.py

# Terminal 2: Start monitoring (optional)
python scripts/line_monitoring/monitor_enhanced.py --week 8

# In Slack: Use commands
# /analyze_props
# /build_parlays
# /line_movement
```

---

## Key Files & Directories

```
nfl-betting-system/
├── scripts/
│   ├── run_analysis.py              ← MAIN COMMAND
│   ├── analyze_parlay_bets.py       ← Calibration analysis
│   ├── generate_betting_card.py     ← Format betting card
│   ├── fetch_odds.py                ← Get fresh odds
│   ├── clear_all_cache.py           ← Clear cache
│   ├── slack_bot/
│   │   └── app_enhanced.py          ← Start Slack bot
│   ├── line_monitoring/
│   │   └── monitor_enhanced.py      ← Line movement monitoring
│   └── analysis/
│       ├── orchestrator.py          ← 8-agent system
│       └── data_loader.py           ← Load & transform data
│
├── data/
│   ├── NFL_roster - Sheet1.csv      ← Player roster
│   ├── wk8_betting_lines_draftkings.csv ← This week's odds
│   ├── week8_betting_card.txt       ← OUTPUT: Your parlays
│   ├── PARLAY_BET_TRACKER.csv       ← Track your bets
│   └── [Weekly DVOA/stats files]
│
├── quick_diagnostic.py              ← Check for missing players
├── find_name_mismatches.py          ← Debug name issues
├── build_enhanced_roster.py         ← Auto-generate roster
├── fix_marquise_brown.py            ← Fix specific players
└── requirements.txt                 ← All dependencies
```

---

## Tips & Best Practices

### Before Running Analysis
```bash
# 1. Verify your roster is complete
python quick_diagnostic.py

# 2. Check for stale data
python scripts/clear_all_cache.py

# 3. Verify environment
python diagnose_env.py
```

### Reduce Command Typing

**Create aliases (Windows PowerShell)**
```powershell
# Add to $PROFILE:
Set-Alias analyze "python scripts/run_analysis.py --week 8 --skip-fetch"
Set-Alias diagnostic "python quick_diagnostic.py"
Set-Alias calibrate "python scripts/analyze_parlay_bets.py"
```

**Create aliases (macOS/Linux bash)**
```bash
# Add to ~/.bashrc or ~/.zshrc:
alias analyze="python scripts/run_analysis.py --week 8 --skip-fetch"
alias diagnostic="python quick_diagnostic.py"
alias calibrate="python scripts/analyze_parlay_bets.py"
```

### Monitor Multiple Terminals

```bash
# Terminal 1: Run analysis
python scripts/run_analysis.py --week 8

# Terminal 2: Monitor lines
python scripts/line_monitoring/monitor_enhanced.py --week 8

# Terminal 3: Start Slack bot (optional)
python scripts/slack_bot/app_enhanced.py
```

---

## Environment Variables

Set these in your `.env` file:

```bash
# The Odds API
ODDS_API_KEY=your_api_key_here

# Slack Bot (if using)
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token

# System settings
NFL_WEEK=8
LOG_LEVEL=INFO
```

---

## Troubleshooting Commands

**System won't run?**
```bash
python diagnose_env.py
```

**Props not loading?**
```bash
python quick_diagnostic.py
python find_name_mismatches.py
python scripts/verify_loader.py
```

**Old data being used?**
```bash
python scripts/clear_all_cache.py
python scripts/run_analysis.py --week 8 --skip-fetch
```

**Need fresh odds?**
```bash
python scripts/run_analysis.py --week 8  # (without --skip-fetch)
```

---

## Quick Copy-Paste Commands

### Start Fresh Analysis
```bash
python scripts/clear_all_cache.py && python scripts/run_analysis.py --week 8 --skip-fetch
```

### Full Diagnostics
```bash
python diagnose_env.py && python quick_diagnostic.py && python scripts/verify_loader.py
```

### Sunday Workflow (One Command)
```bash
# Run this, then manually place bets and update tracker
python scripts/run_analysis.py --week 8 --skip-fetch && cat data/week8_betting_card.txt
```

### Friday Calibration (One Command)
```bash
# After updating tracker with results:
python scripts/analyze_parlay_bets.py
```

---

**Last Updated:** October 25, 2025

For more details, see individual script help:
```bash
python scripts/run_analysis.py --help
python scripts/analyze_parlay_bets.py --help
```
