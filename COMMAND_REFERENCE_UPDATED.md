# NFL Betting System - Command Reference Guide

Complete list of all commands you can run for your NFL betting analysis system.

---

## 📋 Table of Contents

1. [Core Analysis Commands](#core-analysis-commands)
2. [DraftKings-Specific Commands](#draftkings-specific-commands)
3. [Data & Roster Management](#data--roster-management)
4. [Slack Bot & Monitoring](#slack-bot--monitoring)
5. [Betting & Tracking](#betting--tracking)
6. [Diagnostics & Debugging](#diagnostics--debugging)
7. [Weekly Workflow](#weekly-workflow)

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

## DraftKings-Specific Commands

⭐ **NEW FEATURE:** Filter odds by specific bookmaker

### **Fetch DraftKings Lines Only**

```bash
# Fresh DraftKings odds
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings

# Cached DraftKings odds (fast, no API call)
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

### **Fetch Other Sportsbooks**

**FanDuel Only**
```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker fanduel
```

**BetRivers Only**
```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker betrivers
```

**PointsBet Only**
```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker pointsbetau
```

**MyBookie Only**
```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker mybookie
```

**BetOnline Only**
```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker betonline
```

**Bovada Only**
```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker bovada
```

### **All Bookmakers (Default)**

```bash
python scripts/run_analysis_draftkings.py --week 8
```

### **Compare Multiple Sportsbooks**

```bash
# Generate parlays from each book
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
python scripts/run_analysis_draftkings.py --week 8 --bookmaker fanduel
python scripts/run_analysis_draftkings.py --week 8 --bookmaker betrivers

# Compare the 3 betting cards:
# - week8_betting_card.txt (if default)
# - Saved with bookmaker prefix if filtered
```

### **Output Files by Bookmaker**

```
All books:        data/betting_lines_wk_8_live.csv
DraftKings only:  data/betting_lines_wk_8_draftkings.csv
FanDuel only:     data/betting_lines_wk_8_fanduel.csv
```

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

---

## Diagnostics & Debugging

### System Diagnostics

**Check environment and all API keys**
```bash
python diagnose_env.py
```

### Test The Odds API Connection

**Test API with bookmaker filtering**
```bash
python scripts/api/odds_api_enhanced.py
```

**Shows:**
- API quota remaining
- Available bookmakers
- Props from all vs individual books

### Verify Data Loader

**Test data loading pipeline**
```bash
python scripts/verify_loader.py
```

### Test System End-to-End

**Run full system test**
```bash
python test_system.py
```

### Clear Python Cache

**Clear all cached data (fixes stale data issues)**
```bash
python scripts/clear_all_cache.py
```

---

## Weekly Workflow

### Complete Sunday Workflow

```bash
# 1. Generate fresh DraftKings parlays
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings

# 2. Review output in terminal and in:
#    data/week8_betting_card.txt

# 3. Place 10 parlays on DraftKings

# 4. Log them in the tracker
#    Open: data/PARLAY_BET_TRACKER.csv
#    Add rows for each parlay placed

# 5. Start line monitoring (optional, in separate terminal)
python scripts/line_monitoring/monitor_enhanced.py --week 8
```

### Alternative: Multi-Sportsbook Workflow

```bash
# Compare odds across all major sportsbooks
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
python scripts/run_analysis_draftkings.py --week 8 --bookmaker fanduel
python scripts/run_analysis_draftkings.py --week 8 --bookmaker betrivers

# Review the 3 different betting cards
# Place bets where lines are most favorable for each parlay
```

### Friday End-of-Week Analysis

```bash
# 1. Update tracker with results
#    Open: data/PARLAY_BET_TRACKER.csv
#    Fill in: Result (WON/LOST/PUSH), etc.

# 2. Generate calibration report
python scripts/analyze_parlay_bets.py

# 3. Review to understand performance by tier
```

---

## Quick Copy-Paste Commands

### Sunday DraftKings Workflow (One Command)

```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings && cat data/week8_betting_card.txt
```

### Fresh Fetch (All Bookmakers)

```bash
python scripts/run_analysis.py --week 8
```

### Quick Diagnostics

```bash
python quick_diagnostic.py && python scripts/api/odds_api_enhanced.py
```

### Full Analysis (DraftKings + Monitoring)

```bash
# Terminal 1:
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings

# Terminal 2:
python scripts/line_monitoring/monitor_enhanced.py --week 8

# Terminal 3:
python scripts/slack_bot/app_enhanced.py
```

---

## API & Bookmaker Commands

### Check API Quota

```bash
python -c "from scripts.api.odds_api_enhanced import OddsAPI; import logging; logging.basicConfig(level=logging.INFO); api = OddsAPI(); print(api.check_api_quota())"
```

### List Available Bookmakers

```bash
python -c "from scripts.api.odds_api_enhanced import OddsAPI; api = OddsAPI(); print(api.list_available_bookmakers())"
```

### Fetch Specific Markets Only (Save Quota)

```bash
# Core markets only (fewer API results)
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
```

---

## Common Scenarios

### Scenario 1: DraftKings Sunday Analysis

```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
# Then place bets and log in tracker
```

### Scenario 2: Compare Sportsbooks

```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
python scripts/run_analysis_draftkings.py --week 8 --bookmaker fanduel
python scripts/run_analysis_draftkings.py --week 8 --bookmaker betrivers
# Review each week8_betting_card.txt variant
```

### Scenario 3: Troubleshooting Missing Props

```bash
python quick_diagnostic.py
python find_name_mismatches.py
python scripts/clear_all_cache.py
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

### Scenario 4: Friday Calibration

```bash
# After updating tracker with results:
python scripts/analyze_parlay_bets.py
```

---

## Key Files & Directories

```
nfl-betting-system/
├── scripts/
│   ├── run_analysis.py              ← Original (all bookmakers)
│   ├── run_analysis_draftkings.py   ← NEW! (with bookmaker filter)
│   ├── analyze_parlay_bets.py       ← Calibration analysis
│   ├── slack_bot/
│   │   └── app_enhanced.py          ← Start Slack bot
│   ├── line_monitoring/
│   │   └── monitor_enhanced.py      ← Line movement monitoring
│   ├── api/
│   │   ├── odds_api.py              ← Original API client
│   │   └── odds_api_enhanced.py     ← NEW! (with bookmaker filter)
│   └── analysis/
│       ├── orchestrator.py          ← 8-agent system
│       └── data_loader.py           ← Load & transform data
│
├── data/
│   ├── NFL_roster - Sheet1.csv      ← Player roster
│   ├── betting_lines_wk_8_live.csv  ← All bookmakers
│   ├── betting_lines_wk_8_draftkings.csv ← DraftKings only
│   ├── week8_betting_card.txt       ← OUTPUT: Your parlays
│   └── PARLAY_BET_TRACKER.csv       ← Track your bets
│
├── quick_diagnostic.py              ← Check for missing players
├── build_enhanced_roster.py         ← Auto-generate roster
├── COMMAND_REFERENCE.md             ← This file!
└── ODDS_API_DRAFTKINGS_GUIDE.md     ← DraftKings guide
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

## Bookmaker Reference

**Available Sportsbooks:**
- `draftkings` - DraftKings (most popular)
- `fanduel` - FanDuel
- `pointsbetau` - PointsBet
- `betrivers` - BetRivers
- `mybookie` - MyBookie
- `betonline` - BetOnline
- `bovada` - Bovada

**Example - Get only DraftKings lines:**
```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
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
python scripts/verify_loader.py
```

**Old data being used?**
```bash
python scripts/clear_all_cache.py
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
```

**API connection issues?**
```bash
python scripts/api/odds_api_enhanced.py
```

---

## Important Notes

✅ **New Feature:** DraftKings filtering is now available
✅ **Backward Compatible:** Old commands still work
✅ **Same Quota:** Filtering costs same as fetching all
✅ **Recommended:** Use `run_analysis_draftkings.py` for new workflows

---

**Last Updated:** October 25, 2025

For DraftKings-specific details, see: `ODDS_API_DRAFTKINGS_GUIDE.md`
