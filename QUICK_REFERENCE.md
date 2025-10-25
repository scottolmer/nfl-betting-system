# 🎯 MERGED SYSTEM - QUICK REFERENCE CARD

---

## ⚡ START SYSTEM (3 Commands)

```bash
# Terminal 1
python scripts\slack_bot\app_enhanced.py

# Terminal 2
ngrok http 3000

# Terminal 3
python scripts\line_monitoring\monitor_enhanced.py
```

---

## 💬 SLACK COMMANDS

| Command | What It Does |
|---------|--------------|
| `/analyze_props 7` | Top 10 props with confidence |
| `/check_confidence Justin Jefferson` | Player analysis |
| `/build_parlays 7` | Generate 6 parlays |
| `/line_movement` | Recent movements |
| `/fetch_odds 7` | Get latest odds |
| `/system_status` | Health check |
| `/betting_help` | Show all commands |

---

## 🎯 CONFIDENCE LEVELS

| Score | Rating | Emoji | Action |
|-------|--------|-------|--------|
| 75+ | ELITE | 🔥 | Max bet |
| 70-74 | HIGH | ⭐ | Strong |
| 65-69 | GOOD | ✅ | Standard |
| 60-64 | MODERATE | 📊 | Small |
| <60 | LOW | ⚠️ | Pass |

---

## 📁 WHICH FILES TO USE

✅ **USE THESE (Enhanced):**
- `scripts/slack_bot/app_enhanced.py`
- `scripts/line_monitoring/monitor_enhanced.py`

❌ **DON'T USE (Old):**
- `scripts/slack_bot/app_claude.py`
- `scripts/line_monitoring/monitor_main.py`

---

## 🧪 TEST SYSTEM

```bash
# Quick test
python scripts\test_merged_system.py

# Or double-click
TEST_SYSTEM.bat
```

---

## 📚 DOCUMENTATION

| File | Read When |
|------|-----------|
| **README_MERGED.md** | First time setup |
| **MERGED_SYSTEM_GUIDE.md** | Full usage guide |
| **PROJECT_SUMMARY.md** | Technical details |
| **NEW_SESSION_SETUP.md** | New chat session |

---

## 🔧 QUICK FIXES

**Slack not responding?**
```bash
# Use enhanced version
python scripts\slack_bot\app_enhanced.py
```

**No confidence in alerts?**
```bash
# Use enhanced monitor
python scripts\line_monitoring\monitor_enhanced.py
```

**Tests failing?**
```bash
# Check .env has all keys
notepad .env
```

---

## 🎯 DAILY WORKFLOW

**Morning:**
1. Start 3 terminals
2. `/system_status`
3. `/analyze_props 7`

**During Day:**
- Auto line alerts
- `/check_confidence` players
- `/build_parlays` when ready

---

## 💰 SYSTEM COMPONENTS

✅ 8-agent analysis  
✅ Confidence scoring (0-100)  
✅ Parlay builder (6 parlays)  
✅ Line monitoring  
✅ Slack bot  
✅ The Odds API  

---

## 🔥 MERGED = ULTIMATE

**Oct 21 + Oct 22 = The Best! 🏆**

---

*For details, see README_MERGED.md*
