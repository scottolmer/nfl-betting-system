# ⚡ DraftKings Integration - Quick Start Card

## 🎯 TL;DR

Yes, The Odds API supports DraftKings-only filtering. Here's how to use it:

```bash
# DraftKings lines only
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings

# All sportsbooks
python scripts/run_analysis_draftkings.py --week 8

# Compare multiple books
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
python scripts/run_analysis_draftkings.py --week 8 --bookmaker fanduel
```

---

## ✅ Supported Sportsbooks

```
draftkings     ⭐ Recommended (most props)
fanduel
pointsbetau
betrivers
mybookie
betonline
bovada
```

---

## 📊 What You Get

**Saved Files:**
```
All books:       betting_lines_wk_8_live.csv
DraftKings:      betting_lines_wk_8_draftkings.csv
FanDuel:         betting_lines_wk_8_fanduel.csv
Etc.
```

**Generated:**
```
Betting card with 10 optimized parlays
Specific to whichever sportsbook you chose
```

---

## 🚀 Sunday Workflow

```bash
# 1. Get DraftKings lines (fresh odds)
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings

# 2. Review betting card
cat data/week8_betting_card.txt

# 3. Place 10 parlays on DraftKings

# 4. Log in tracker
# (Edit: data/PARLAY_BET_TRACKER.csv)
```

---

## 📚 Full Documentation

- **`DRAFTKINGS_INTEGRATION_SUMMARY.md`** - Complete overview
- **`ODDS_API_DRAFTKINGS_GUIDE.md`** - Detailed guide
- **`COMMAND_REFERENCE_UPDATED.md`** - All commands

---

## 🧪 Test It

```bash
python scripts/api/odds_api_enhanced.py
```

Shows all available bookmakers and lets you compare.

---

## 💡 Three Ways to Use

### Way 1: DraftKings Only (Recommended)
```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
```

### Way 2: Compare Multiple Books
```bash
# Generate from each
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
python scripts/run_analysis_draftkings.py --week 8 --bookmaker fanduel
python scripts/run_analysis_draftkings.py --week 8 --bookmaker betrivers

# Compare betting cards, place bets where lines are best
```

### Way 3: All Sportsbooks (Original Behavior)
```bash
python scripts/run_analysis_draftkings.py --week 8
# Same as old: python scripts/run_analysis.py --week 8
```

---

## ❓ Common Questions

**Q: Extra API cost?**
No - filtering is free.

**Q: Do I need to update my old script?**
No - `run_analysis.py` still works. This is optional.

**Q: Which book to choose?**
DraftKings has best coverage. FanDuel is second. Compare if you want.

**Q: Can I use cached data?**
Yes - `--skip-fetch` works: `python scripts/run_analysis_draftkings.py --week 8 --skip-fetch`

---

**Ready? Start with:**
```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings
```

**Questions? Read:**
```
DRAFTKINGS_INTEGRATION_SUMMARY.md
```
