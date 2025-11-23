# 🏈 Parlay Validation UI

Visual interface for validating parlays against DraftKings Pick6 availability.

---

## Quick Start

### Windows (Easiest)
```
run_validation_ui.bat
```
Double-click the file, and the UI opens in your browser.

### Command Line
```bash
streamlit run validation_ui.py
```

Opens at: `http://localhost:8501`

---

## What It Does

1. **Loads** betting lines and analyzes props
2. **Builds** 10 optimized parlays
3. **Shows** each parlay visually
4. **Lets you check** if props are on DK Pick6
5. **Learns** which props are available
6. **Rebuilds** parlays using only valid props

---

## How to Use (3 Steps)

### 1. Load Data
- Select week (e.g., 12)
- Click "📊 Load & Generate Parlays"
- Wait ~10-30 seconds

### 2. Validate Parlays
For each parlay:
- ✓ Check boxes if props are available
- ☐ Uncheck if NOT available
- Click:
  - **✅ Accept All** (all available)
  - **❌ Mark Invalid Props** (some unavailable)
  - **⏭️ Skip** (not sure)

### 3. Rebuild
- After all validated, click **"🔨 Rebuild Parlays"**
- Get 10 final parlays ready for DK Pick6

---

## UI Layout

```
┌─────────────────────────────┬─────────────────────────────┐
│ Sidebar                     │ Main Area                   │
├─────────────────────────────┼─────────────────────────────┤
│ Week: [12]                  │ 📊 2-LEG Parlay #1         │
│ [📊 Load & Generate]        │ Confidence: 71%             │
│                             │                             │
│ Statistics:                 │ Props:                      │
│ • Total: 10                 │ 1. Josh Allen               │
│ • Validated: 3              │    Pass Yds OVER 275.5      │
│ • Remaining: 7              │    [✓] Available            │
│ [====>    ] 30%             │                             │
│                             │ 2. Stefon Diggs             │
│ System Stats:               │    Rec Yds OVER 75.5        │
│ • Rules: 4                  │    [✓] Available            │
│ • Available: 127            │                             │
│ • Unavailable: 23           │ [✅ Accept][❌ Mark][⏭️ Skip]│
└─────────────────────────────┴─────────────────────────────┘
```

---

## Features

✅ **Visual validation** - See props clearly
✅ **Progress tracking** - Real-time progress bar
✅ **One-click actions** - Accept/Reject with buttons
✅ **Auto-learning** - System remembers your choices
✅ **Rule filtering** - Auto-rejects known bad combos
✅ **Statistics dashboard** - See validation stats
✅ **Automatic rebuild** - Creates new parlays from valid props

---

## Example Session

```
1. Run: run_validation_ui.bat
2. Browser opens automatically
3. Select week: 12
4. Click "Load & Generate Parlays"
5. First parlay appears
6. Check DraftKings Pick6 app
7. Mark props as available/unavailable
8. Click Accept/Mark Invalid
9. Repeat for each parlay
10. Click "Rebuild Parlays"
11. View final 10 validated parlays
```

**Time:** 5-10 minutes for full validation

---

## Advantages Over CLI

| Feature | CLI | UI |
|---------|-----|-----|
| Visual | ❌ Text | ✅ Graphics |
| Progress | ❌ Manual | ✅ Auto bar |
| Prop toggle | ❌ Type numbers | ✅ Checkboxes |
| Stats | ❌ Text dump | ✅ Dashboard |
| Ease | ❌ Commands | ✅ Clicks |

---

## Tips

💡 **Open DK Pick6 first** - Have it ready in another window
💡 **Default all checked** - Only uncheck unavailable props
💡 **Use Skip** - If you're unsure about a parlay
💡 **Watch progress** - Progress bar shows how many left
💡 **System learns** - Each validation makes next week easier

---

## Troubleshooting

**UI won't start?**
```bash
pip install streamlit
streamlit run validation_ui.py
```

**No parlays generated?**
- Make sure betting lines CSV exists for that week
- Check `data/` folder for `betting_lines_wk_12_*.csv`

**Want to start over?**
- Click "Load & Generate Parlays" again
- Resets validation for that session

---

## Documentation

- **This file** - Quick start
- **docs/VALIDATION_UI_GUIDE.md** - Complete guide
- **HOW_TO_USE_VALIDATION.md** - General validation guide

---

## Technical Details

- **Framework:** Streamlit 1.50.0
- **Backend:** Existing validation system
- **Database:** `bets.db` (shared with CLI)
- **Port:** 8501 (default)

---

## Stop the UI

Press **Ctrl+C** in the terminal to stop the server.

---

## You're Ready!

Just run:
```
run_validation_ui.bat
```

And follow the on-screen instructions!
