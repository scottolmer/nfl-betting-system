# Odds API Live Integration - Setup Guide

## Overview

Your betting system now has **live Odds API integration** that runs automatically on every analysis command.

## Changes Made

### 1. **New CLI with Live Odds**
- **File**: `betting_cli_odds_integrated.py`
- Fetches fresh props from The Odds API before every `analyze` command
- New `odds` command to check API quota

### 2. **Updated `fetch_odds_silent.py`**
- Now actually calls The Odds API instead of just validating CSV files
- Falls back to existing CSV data if API call fails
- Automatically caches results to CSV

### 3. **How It Works**

```
analyze <query>
    ↓
fetch_fresh_odds()
    ↓
OddsAPI.get_player_props()
    ↓
Save to betting_lines_wk_{week}_live.csv
    ↓
Query handler analyzes with fresh data
```

## Prerequisites

### 1. Set API Key in `.env`
```
ODDS_API_KEY=your_api_key_here
```

### 2. Verify Installation
```bash
# Test Odds API connection
python scripts/api/odds_api.py
```

Expected output:
```
API Requests - Used: X, Remaining: Y
Found N NFL events
Found M props
✅ API TEST SUCCESSFUL!
```

## Usage

### Run with Live Odds

```bash
# Use the new integrated CLI
python betting_cli_odds_integrated.py
```

### Example Workflow

```
📊 Enter command: analyze Jordan Love 275 pass yards
📡 Connecting to The Odds API...
   Requests available: 498
   Fetching live player props...
✅ Fetched 2847 live props

🔄 Analyzing: Jordan Love 275 pass yards...
[analysis results]
```

### Check API Quota

```
📊 Enter command: odds

📊 Odds API Quota Status
   Requests used: 2
   Requests remaining: 498
```

### Generate Parlays with Fresh Odds

```
📊 Enter command: parlays 65
📡 Fetching fresh odds for Week 8...
✅ Fetched X live props
🏵 Fetching fresh injury data...
🔄 Loading data and analyzing all props...
```

## API Quotas

The Odds API provides:
- **Free Tier**: 500 requests/month
- **Premium Tier**: Based on subscription

Each `analyze` command uses **1 API request**.
Each `parlays` command uses **1 API request**.

## Troubleshooting

### "ODDS_API_KEY not found"
→ Add `ODDS_API_KEY=your_key` to `.env` file

### API returns no data
→ Check if markets are available for current week
→ Falls back to existing CSV data automatically

### Want to use old CLI temporarily?
```bash
python betting_cli.py  # Uses existing CSV only
```

## What Changed from Original

| Feature | Before | Now |
|---------|--------|-----|
| Data freshness | Uses cached CSV | Fetches fresh on every analyze |
| API Integration | Validation only | Active fetching & caching |
| Error handling | Silent failure | Graceful fallback to cached data |
| Quota visibility | Hidden | `odds` command shows status |

## Next Steps

1. ✅ Update `.env` with your ODDS_API_KEY
2. ✅ Test with: `python scripts/api/odds_api.py`
3. ✅ Run new CLI: `python betting_cli_odds_integrated.py`
4. ✅ Try analyze command: `analyze Mahomes 275 pass yards`

## Advanced: Customize Markets

Edit the `OddsAPI.get_player_props()` call in `betting_cli_odds_integrated.py`:

```python
props = self.odds_api.get_player_props(
    markets='player_pass_yds,player_rush_yds,player_receptions,player_reception_yds'
)
```

Available markets:
- `player_pass_tds`, `player_pass_yds`, `player_pass_completions`
- `player_rush_yds`, `player_rush_attempts`
- `player_receptions`, `player_reception_yds`
- `player_touchdowns`, `player_kicking_points`
