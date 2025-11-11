# Quick Setup: RotoWire Injury Scraper

## 1️⃣ Install Required Package

```bash
pip install beautifulsoup4
```

## 2️⃣ Test the Scraper

```bash
python scripts/fetch_rotowire_injuries.py --week 8
```

Should output:
```
ROTOWIRE INJURY REPORT SCRAPER
✅ Found X injuries
✅ Saved to: data/wk8-injury-report.csv
```

## 3️⃣ Run Your Full Analysis (Auto-Fetches Injuries)

```bash
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

**What happens automatically:**
1. Fetches latest injuries from RotoWire
2. Loads betting lines
3. Analyzes props (injury-aware)
4. Builds 10 parlays
5. Opens betting card

---

## 🎯 Updated Commands

### Sunday Workflow (With Auto-Injuries)

```bash
# Fetch latest injuries + analyze
python scripts/run_analysis_draftkings.py --week 8 --skip-fetch
```

### Manual Injury Fetch Only

```bash
python scripts/fetch_rotowire_injuries.py --week 8
```

### Skip Auto-Injury Fetch

```bash
python scripts/run_analysis_draftkings.py --week 8 --skip-injuries --skip-fetch
```

### With DraftKings Bookmaker Filter (Auto-Injuries)

```bash
python scripts/run_analysis_draftkings.py --week 8 --bookmaker draftkings --skip-fetch
```

---

## 📄 Documentation

Full guide: `ROTOWIRE_INJURY_SCRAPER_GUIDE.md`

---

**That's it! Your system now auto-fetches injuries every time you run analysis.** 🏥
