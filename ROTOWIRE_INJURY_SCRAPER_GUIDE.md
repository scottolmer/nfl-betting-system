# RotoWire Injury Report Auto-Scraper Setup Guide

## 🏥 What This Does

Automatically fetches the latest NFL injury data from RotoWire and integrates it into your analysis system.

**Before:** You manually downloaded injury reports  
**After:** It automatically fetches and updates before each analysis

---

## 📦 Installation

### Step 1: Install Required Package

```bash
pip install beautifulsoup4 requests
```

That's it! You now have:
- `beautifulsoup4` - Web scraping library
- `requests` - HTTP library (probably already have it)

### Step 2: Verify Installation

```bash
python -c "import bs4; print('✅ beautifulsoup4 installed')"
```

---

## 🚀 How to Use

### Automatic (Recommended)

The injury scraper runs automatically with your analysis:

```bash
# Fetches injuries from RotoWire, then runs analysis
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

**What happens:**
1. ✅ Fetches latest injuries from RotoWire
2. ✅ Saves to `data/wk8-injury-report.csv`
3. ✅ Loads into analysis system
4. ✅ Analyzes all props (injury-aware)
5. ✅ Generates betting card
6. ✅ Opens betting card automatically

### Manual

If you want to fetch injuries separately:

```bash
python scripts/fetch_rotowire_injuries.py --week 8
```

**Output:**
```
ROTOWIRE INJURY REPORT SCRAPER
======================================================================

Fetching injuries from RotoWire...
✅ Found 45 injuries
✅ Saved to: data/wk8-injury-report.csv

Injury Report Preview (45 total):
----------------------------------------------------------------------
Player               Team  Position  Status        Details          Date
Kirk Cousins         ATL   QB        Out           Hamstring       2025-10-25
Jaylen Warren        PIT   RB        Questionable  Ankle           2025-10-25
Chris Jones          KC    DL        Out           Wrist           2025-10-25
...
```

### Skip Injuries (if you want to use manual reports)

```bash
# Don't fetch injuries, use manual injury report
python scripts/run_analysis_draftkings.py --week 8 --skip-injuries --skip-fetch
```

---

## 📊 Output Files

The scraper creates:

```
data/wk8-injury-report.csv

Columns:
- Player: Player name
- Team: NFL team abbreviation
- Position: Player position (QB, RB, WR, etc.)
- Status: Out, Questionable, Doubtful, Probable
- Details: Injury type (hamstring, ankle, etc.)
- Date: When injury was reported
```

---

## 🔍 How It Works

1. **Fetches** the RotoWire injury report page
2. **Parses** the HTML table with injury data
3. **Extracts** player, team, position, status, details
4. **Saves** to CSV in your data folder
5. **Your injury agent** automatically uses this data in analysis

**Smart Integration:**
- Your `InjuryAgent` reads this CSV automatically
- Adjusts confidence scores based on injury severity
- Reduces confidence for players with injuries
- Skips analysis for Out/PUP players

---

## ⚠️ Important Notes

### Rate Limiting
- Respectful scraping (identifies as bot, uses delays)
- One request per analysis run
- Won't get blocked by RotoWire

### Fallback Behavior
- If scraping fails, uses your existing injury data
- Never crashes your analysis
- Shows warning but continues

### Data Quality
- RotoWire is highly reliable
- Updates injuries in real-time
- Better than manual CSV updates

---

## 🎯 Typical Sunday Workflow

```bash
# One command does everything:
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch

# What happens automatically:
# 1. Fetches latest injuries from RotoWire
# 2. Loads your cached betting lines
# 3. Analyzes 1140+ props (injury-aware)
# 4. Builds 10 parlays
# 5. Opens betting card
# Result: 2-3 minutes, fully automated
```

---

## 🛠️ Troubleshooting

### "beautifulsoup4 not installed"

```bash
pip install beautifulsoup4
```

### "No injuries found"

1. Check your internet connection
2. Visit https://www.rotowire.com/football/injury-report.php manually
3. Make sure RotoWire is accessible
4. Try again with `--skip-injuries` to use existing data

### "Scraper not available"

Means beautifulsoup4 isn't installed. Run:
```bash
pip install beautifulsoup4
```

### Website structure changed

If RotoWire redesigns their page, the scraper might break. Let me know and I can update the parser.

---

## 📝 File Locations

```
scripts/
├── fetch_rotowire_injuries.py    <- Standalone scraper
└── run_analysis_draftkings.py    <- Main script (uses scraper)

data/
└── wk8-injury-report.csv         <- Latest injuries
```

---

## 🎯 What Changed in Your System

### Before
```bash
python scripts/run_analysis.py --week 8 --skip-fetch
# Loads manual injury report
# Analyzes props
```

### After
```bash
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
# Auto-fetches latest injuries from RotoWire
# Loads betting lines
# Analyzes props (using fresh injury data)
# Opens betting card
```

---

## ✅ Quick Checklist

- [ ] Installed beautifulsoup4: `pip install beautifulsoup4`
- [ ] Tested scraper: `python scripts/fetch_rotowire_injuries.py --week 8`
- [ ] Run full analysis: `python scripts/run_analysis_draftkings.py --week 8 --skip-fetch`
- [ ] See injuries auto-fetched and integrated

---

## 🚀 You're All Set!

Your system now automatically:
1. ✅ Fetches latest injuries from RotoWire
2. ✅ Analyzes props with injury awareness
3. ✅ Generates betting card
4. ✅ Opens automatically

**One command. Everything automated.** 🎉

---

**Questions?** Check the scraper code in `scripts/fetch_rotowire_injuries.py` - it's well documented!
