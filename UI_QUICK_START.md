# 🏈 NFL Betting System - UI Quick Start

## Two UIs Available

### 1. Complete Betting System (Recommended)
**Full dashboard with all features**

```
run_betting_system.bat
```

**Features:**
- 🏠 Dashboard - Overview and top props
- 🎯 Prop Analysis - Filter, sort, browse all props
- 🎲 Parlay Builder - Generate and view parlays
- ✅ Validation - Link to validation tools
- 📊 Performance - Track results
- ⚙️ Settings - Configure system

**Use for:** Complete workflow from analysis to betting

---

### 2. Validation UI (Focused)
**Dedicated parlay validation**

```
run_validation_ui.bat
```

**Features:**
- Load & generate parlays
- Validate against DK Pick6
- Interactive checkboxes
- Auto-rebuild invalid parlays
- Progress tracking

**Use for:** Just validating parlays

---

## Which One to Use?

### Use Complete System When:
- ✅ Starting fresh (need to analyze props)
- ✅ Exploring different players/teams
- ✅ Building custom parlays
- ✅ Tracking performance
- ✅ Want everything in one place

### Use Validation UI When:
- ✅ Already have parlays generated
- ✅ Just need to validate for DK Pick6
- ✅ Want focused, fast validation
- ✅ Teaching system prop availability

---

## Typical Workflow

### Option A: All-in-One (Complete System)
```
1. run_betting_system.bat
2. Load Data (sidebar)
3. Review Props (Prop Analysis page)
4. Generate Parlays (Parlay Builder page)
5. Open Validation UI (Validation page → link)
6. Validate parlays
7. Back to main UI to view results
```

### Option B: Two-Step
```
1. run_betting_system.bat
2. Load Data
3. Generate Parlays
4. Close main UI
5. run_validation_ui.bat
6. Validate parlays
```

---

## Quick Commands

| Task | Command |
|------|---------|
| **Main UI** | `run_betting_system.bat` |
| **Validation UI** | `run_validation_ui.bat` |
| **Stop UI** | Press Ctrl+C in terminal |
| **Restart** | Close and run again |

---

## Ports

- **Main System:** http://localhost:8502
- **Validation UI:** http://localhost:8501

**Note:** Can run both at same time!

---

## First Time Setup

1. **Install dependencies** (if needed):
   ```bash
   pip install streamlit pandas
   ```

2. **Ensure data exists**:
   - Check `data/` folder
   - Need `betting_lines_wk_12_*.csv` files
   - Run `betting_cli.py` → `pull-lines` if missing

3. **Run UI**:
   ```
   run_betting_system.bat
   ```

4. **Load data**:
   - Select week
   - Click "Load Data"
   - Wait ~30 seconds

5. **Start exploring!**

---

## Screenshots Reference

### Main System - Dashboard
```
┌────────────────────────────────────────┐
│ 🏈 NFL Betting System                 │
│                                        │
│ Week: [12] [📊 Load Data]             │
│ ────────────────────                   │
│ Navigation:                            │
│ ● 🏠 Dashboard          Total: 1177   │
│ ○ 🎯 Prop Analysis      High: 207     │
│ ○ 🎲 Parlay Builder     OVER: 588     │
│ ○ ✅ Validation         UNDER: 589    │
│ ○ 📊 Performance                       │
│ ○ ⚙️ Settings           Top 10 Props  │
│                         [Table view]   │
└────────────────────────────────────────┘
```

### Validation UI
```
┌────────────────────────────────────────┐
│ 🏈 Parlay Validator                   │
│                                        │
│ Week: [12] [Load & Generate]          │
│ ────────────────────                   │
│ Total: 10                              │
│ Validated: 5                           │
│ Remaining: 5                           │
│ [======>   ] 50%        📊 2-LEG #6   │
│                                        │
│ System Stats:           Props:         │
│ Rules: 4                1. Josh Allen  │
│ Available: 127             [✓] Available
│ Unavailable: 23         2. Stefon Diggs
│                            [✓] Available
│                                        │
│                         [✅][❌][⏭️]     │
└────────────────────────────────────────┘
```

---

## Tips

💡 **Both UIs share the same database** - Work done in one affects the other
💡 **Main UI for exploration** - Validation UI for speed
💡 **Run both simultaneously** - Different ports, no conflict
💡 **Browser stays open** - Refresh if connection lost

---

## Documentation

| Doc | Purpose |
|-----|---------|
| **This file** | Quick start both UIs |
| `BETTING_SYSTEM_UI_README.md` | Complete system guide |
| `VALIDATION_UI_README.md` | Validation UI guide |
| `docs/VALIDATION_UI_GUIDE.md` | Detailed validation docs |

---

## That's It!

Pick a UI and run it:
- **Full system:** `run_betting_system.bat`
- **Just validation:** `run_validation_ui.bat`

Both work great! Choose based on your needs.
