# DraftKings-Only Betting Lines Integration Guide

## 📋 Overview

The Odds API returns data from **multiple bookmakers**. Now you can filter to specific sportsbooks like DraftKings, FanDuel, BetRivers, etc.

---

## 🎯 Quick Start - DraftKings Only

### **Option 1: Use New Enhanced Script (Recommended)**

```bash
# Fetch fresh odds from DraftKings only
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings

# Use cached data
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

### **Option 2: Use Enhanced API Directly**

```python
from scripts.api.odds_api_enhanced import OddsAPI

api = OddsAPI()

# DraftKings only
props = api.get_player_props(bookmaker='draftkings')

# FanDuel only
props = api.get_player_props(bookmaker='fanduel')

# All bookmakers (default)
props = api.get_player_props()
```

---

## 📚 Available Bookmakers

The Odds API has many sportsbooks available:

```
✅ draftkings      - DraftKings
✅ fanduel         - FanDuel
✅ pointsbetau     - PointsBet
✅ betrivers       - BetRivers
✅ mybookie        - MyBookie
✅ betonline       - BetOnline
✅ bovada          - Bovada
```

---

## 🔧 Command Examples

### **Fetch DraftKings Lines**

```bash
# Fresh DraftKings lines
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings

# Cached DraftKings lines
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

### **Fetch FanDuel Lines**

```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker fanduel
```

### **Fetch All Bookmakers**

```bash
# Default behavior
python scripts/run_analysis_draftkings.py --week 8
```

### **Compare Bookmakers**

```bash
# Generate parlays from each bookmaker
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
python scripts/run_analysis_draftkings.py --week 8 --bookmaker fanduel
python scripts/run_analysis_draftkings.py --week 8 --bookmaker betrivers

# Compare the 3 betting cards generated
```

---

## 📊 What Gets Saved

When you fetch with a bookmaker filter, the system saves it with a unique filename:

```
# DraftKings
data/betting_lines_wk_8_draftkings.csv

# FanDuel
data/betting_lines_wk_8_fanduel.csv

# All bookmakers (default)
data/betting_lines_wk_8_live.csv
```

---

## 🔍 API Details

### **The Odds API Response Structure**

```
Event (Game)
  └── Bookmakers (DraftKings, FanDuel, etc.)
      └── Markets (Pass Yds, Rec Yds, etc.)
          └── Outcomes (Over/Under with odds)
```

**Your old system:** Got props from ALL bookmakers in the response
**New system:** Can filter to just DraftKings (or any sportsbook)

### **Available Markets**

All bookmakers have these player prop markets:

```
Pass Stats:
- player_pass_tds       ← Pass TDs
- player_pass_yds       ← Pass Yards
- player_pass_completions
- player_pass_attempts

Rush Stats:
- player_rush_yds       ← Rush Yards
- player_rush_attempts

Receiving Stats:
- player_receptions     ← Receptions
- player_reception_yds  ← Receiving Yards
- player_rush_reception_yds

Other:
- player_touchdowns
- player_kicking_points
```

---

## 💡 Use Cases

### **Case 1: You Only Bet on DraftKings**

```bash
# Sunday workflow
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings

# Rest of week (cached)
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

### **Case 2: Compare Across Sportsbooks**

```bash
# Generate from each sportsbook
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
python scripts/run_analysis_draftkings.py --week 8 --bookmaker fanduel
python scripts/run_analysis_draftkings.py --week 8 --bookmaker betrivers

# Compare output files:
# - week8_betting_card_draftkings.txt
# - week8_betting_card_fanduel.txt
# - week8_betting_card_betrivers.txt
```

### **Case 3: Find Best Lines Across Books**

Run against each book, then use the comparison to decide:
- "DraftKings has the best -110 odds on this prop"
- "FanDuel has a +0.5 edge on this player's yards"

### **Case 4: Arbitrage Opportunities**

Detect when the same prop has different lines across books:

```bash
# DraftKings: Player Rec Yds OVER 65.5 @ -110
# FanDuel: Player Rec Yds OVER 65.5 @ -120

# Can identify which book offers better value
```

---

## 🚀 Integration with Your System

### **Updated Files**

1. **`scripts/api/odds_api_enhanced.py`** ← Enhanced API client
2. **`scripts/run_analysis_draftkings.py`** ← New analysis script with bookmaker support

### **Backward Compatible**

Your existing scripts still work:

```bash
# Old command still works (uses all bookmakers)
python scripts/run_analysis.py --week 8

# New command with bookmaker filtering
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
```

---

## 📝 API Usage & Quota

### **One API Request Returns All Data**

When you call `get_player_props()`:
- ✅ **1 API request** = all bookmakers + all markets for that week
- ✅ Filtering by bookmaker happens **locally** (no extra requests)
- ✅ Same quota cost whether you filter or not

### **Your Free Tier**

```
500 requests/month (plenty for weekly use)

Sunday: 1 request (fetch fresh odds)
Monitoring: ~30 requests/month (hourly checks)
Testing: Leftover quota
```

---

## 🧪 Testing the Integration

### **Test DraftKings Filtering**

```bash
python scripts/api/odds_api_enhanced.py
```

This will show:
- ✅ API quota status
- ✅ Available bookmakers
- ✅ Total props from all books
- ✅ Comparison: All vs DraftKings vs FanDuel

### **Output Example**

```
📊 Checking API quota...
   Requests remaining: 498
   Requests used: 2

📚 Available bookmakers:
   - draftkings
   - fanduel
   - pointsbetau
   - betrivers
   - mybookie
   - betonline
   - bovada

🎯 Fetching props from ALL bookmakers...
   Found 6147 total props

   Props by bookmaker:
      draftkings: 2150
      fanduel: 1950
      pointsbetau: 850
      betrivers: 1197

⭐ Fetching props from DRAFTKINGS ONLY...
   Found 2150 DraftKings props
```

---

## 🎯 Recommended Workflow

```bash
# Sunday Morning: Get fresh DraftKings lines
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings

# Review betting card
cat data/week8_betting_card.txt

# Place 10 parlays on DraftKings

# Log in tracker
# (Edit: data/PARLAY_BET_TRACKER.csv)

# Monday-Thursday: Use cached data if tweaking
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch

# Friday: Analyze results
python scripts/analyze_parlay_bets.py
```

---

## 🔧 Troubleshooting

### **"Module not found: odds_api_enhanced"**

Make sure both files exist:
- ✅ `scripts/api/odds_api_enhanced.py`
- ✅ `scripts/run_analysis_draftkings.py`

Falls back to original API if not found.

### **"Invalid bookmaker"**

Valid options:
```
draftkings, fanduel, pointsbetau, betrivers, mybookie, betonline, bovada
```

### **No props returned from DraftKings**

```bash
# Check if DraftKings actually has lines for this week
# Try all bookmakers to verify API is working
python scripts/run_analysis_draftkings.py --week 8

# Then check DraftKings specifically
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
```

---

## 📖 The Odds API Documentation

Full docs: https://the-odds-api.com/

Key concepts:
- **Regions:** 'us' = American odds
- **Markets:** Player prop types (pass_yds, rec_yds, etc.)
- **Bookmakers:** Individual sportsbooks available
- **Odds Format:** 'american' = -110, +210 style

---

## 💾 Updated Command Reference

Add these to your `COMMAND_REFERENCE.md`:

### **DraftKings-Specific Analysis**

```bash
# Fetch fresh DraftKings lines and generate parlays
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings

# Use cached DraftKings lines
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch

# Fetch FanDuel lines
python scripts/run_analysis_draftkings.py --week 8 --bookmaker fanduel

# Compare bookmakers
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
python scripts/run_analysis_draftkings.py --week 8 --bookmaker fanduel
python scripts/run_analysis_draftkings.py --week 8 --bookmaker betrivers
```

---

## ✅ Summary

| Feature | Before | After |
|---------|--------|-------|
| API Integration | ✅ Already had it | ✅ Same |
| Bookmaker Filtering | ❌ No | ✅ Yes |
| DraftKings Only | ❌ No | ✅ Yes |
| Compare Sportsbooks | ❌ No | ✅ Yes |
| API Quota | ✅ Tracked | ✅ Same quota |
| Backward Compatible | N/A | ✅ Yes |

**To answer your original question: YES, The Odds API supports filtering by bookmaker. You now have two scripts to use it:**

1. **Original:** `run_analysis.py` (all bookmakers)
2. **New:** `run_analysis_draftkings.py` (with bookmaker filtering)

Choose whichever fits your workflow!

---

**Questions? Test the enhanced API:**
```bash
python scripts/api/odds_api_enhanced.py
```
