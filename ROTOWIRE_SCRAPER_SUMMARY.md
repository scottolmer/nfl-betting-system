# RotoWire Injury Scraper - What's New

## ✨ What I Built

A **web scraper** that automatically fetches the latest NFL injury data from RotoWire and integrates it into your analysis system.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Beautiful Soup
```bash
pip install beautifulsoup4
```

### Step 2: Test It
```bash
python scripts/fetch_rotowire_injuries.py --week 8
```

### Step 3: Use It (Auto-Integrated)
```bash
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

**That's it!** ✅

---

## 📊 How It Works

**Before:**
```
You → Manually download CSV from RotoWire → Upload to system → Analysis
```

**After:**
```
One command → Auto-fetches RotoWire → Auto-analyzes → Opens betting card
```

---

## 🎯 What Happens When You Run Analysis

```bash
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

**Automatic sequence:**
1. ✅ Fetches latest injuries from RotoWire.com
2. ✅ Saves to `data/wk8-injury-report.csv`
3. ✅ Loads betting lines (cached)
4. ✅ Your injury agent analyzes props (injury-aware)
5. ✅ Builds 10 parlays
6. ✅ Opens betting card

**Total time:** 2-3 minutes  
**User input required:** 0

---

## 📁 Files Created/Updated

### New Files:
- `scripts/fetch_rotowire_injuries.py` - Standalone scraper
- `ROTOWIRE_INJURY_SCRAPER_GUIDE.md` - Full documentation
- `INJURY_SCRAPER_QUICKSTART.md` - Quick reference

### Updated Files:
- `scripts/run_analysis_draftkings.py` - Now auto-fetches injuries

---

## 🔧 Available Options

### Auto-Fetch Injuries (Default)
```bash
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

### Skip Injury Fetch
```bash
python scripts/run_analysis_draftkings.py --week 8 --skip-injuries --skip-fetch
```

### Manual Fetch Only
```bash
python scripts/fetch_rotowire_injuries.py --week 8
```

### Compare Sportsbooks (with auto-injuries)
```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings --skip-fetch
python scripts/run_analysis_draftkings.py --week 8 --bookmaker fanduel --skip-fetch
```

---

## 💡 Smart Integration

Your **InjuryAgent** automatically:
- ✅ Reads the scraped injury CSV
- ✅ Reduces confidence for injured players
- ✅ Skips Out/PUP players
- ✅ Adjusts prop analysis accordingly

**Result:** More accurate confidence scores!

---

## ⚙️ Technical Details

**What it scrapes:**
- Player name
- Team
- Position
- Injury status (Out, Questionable, Doubtful, Probable)
- Injury details (hamstring, ankle, etc.)
- Report date

**Data source:** https://www.rotowire.com/football/injury-report.php

**Update frequency:** Every time you run analysis (realtime data)

**Fallback:** If scraping fails, uses existing injury CSV (never crashes)

---

## ✅ Your Sunday Workflow

**Before:**
```bash
# 1. Download CSV from RotoWire manually
# 2. Upload to system
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

**After:**
```bash
# One command, everything automated
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

---

## 🎉 Summary

You now have:
- ✅ The Odds API integration (DraftKings filtering)
- ✅ 8-agent prop analysis system
- ✅ Auto-fetching betting lines
- ✅ **Auto-fetching injury data** ← NEW
- ✅ Position-diverse parlay building
- ✅ Auto-opening betting card
- ✅ Full tracking infrastructure

**Everything automated. One command.** 🚀

---

## 📚 Documentation

- **Quick start:** `INJURY_SCRAPER_QUICKSTART.md`
- **Full guide:** `ROTOWIRE_INJURY_SCRAPER_GUIDE.md`
- **Commands:** `COMMAND_REFERENCE_UPDATED.md`

---

**Ready to test? Run:**
```bash
pip install beautifulsoup4
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

Injuries will auto-fetch and integrate! 🏥
