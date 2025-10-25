# 🚀 Quick Setup Guide

## Step 1: Install Dependencies

```bash
cd C:\Users\scott\Desktop\nfl-betting-system
pip install -r requirements.txt
```

## Step 2: Configure API Key

Your `.env` file should already exist with your Odds API key. If not, create it:

```bash
# Create .env file
echo ODDS_API_KEY=your_api_key_here > .env
```

Replace `your_api_key_here` with your actual API key.

## Step 3: Test API Connection

```bash
python scripts\api\odds_api.py
```

Expected output:
```
✅ API TEST SUCCESSFUL!
Requests remaining: 499
```

## Step 4: Fetch Live Odds

```bash
python scripts\fetch_odds.py --week 7
```

This will:
- Use 1 API request
- Fetch all player props for Week 7
- Save to `data/betting_lines_wk_7_live.csv`

## Step 5: Generate Betting Card

```bash
python scripts\generate_betting_card.py
```

This will:
- Analyze all props using DVOA + projections
- Generate 6 optimal parlays
- Save to `data/week7_betting_card.txt`

## Alternative: One-Command Workflow

```bash
# Complete analysis (fetch + analyze + generate card)
python scripts\run_analysis.py --week 7

# Or skip API fetch if you already have odds
python scripts\run_analysis.py --week 7 --skip-fetch
```

---

## Troubleshooting

### "ODDS_API_KEY not found"
- Make sure `.env` file exists in the project root
- Check that the file contains: `ODDS_API_KEY=your_key`
- No quotes needed around the key

### "Module not found"
```bash
pip install -r requirements.txt
```

### "API quota exceeded"
- The Odds API has rate limits (check your plan)
- Use `--skip-fetch` to work with existing data
- Each `fetch_odds.py` call uses 1 API request

---

## 📊 What's Included

### Data Files Needed (in `/data` folder):
- ✅ DVOA rankings (Off/Def)
- ✅ Defensive vs position stats
- ✅ Player projections
- ✅ Injury reports
- ✅ Betting lines (from API or manual)

### Generated Files:
- `betting_lines_wk_X_live.csv` - Raw odds from API
- `weekX_betting_card.txt` - Actionable parlays

---

## 🎯 Weekly Workflow

```bash
# Every week, just run:
python scripts\run_analysis.py --week 8
```

That's it! The system will:
1. Fetch live odds (uses 1 API request)
2. Analyze 1,000+ props
3. Generate 6 optimal parlays
4. Save betting card

**Total time: ~2 minutes**

---

## 💡 Tips

- Run in the morning for best lines
- Re-run before games to catch line movements
- Check `--skip-fetch` to save API requests
- Start with 2-leg parlays for higher hit rate

---

Good luck! 🍀
