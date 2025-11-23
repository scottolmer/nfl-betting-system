

# 🏈 NFL Betting System - Complete UI

Full-featured web dashboard for NFL prop betting analysis and parlay generation.

---

## Quick Start

### Windows (Easiest)
```
run_betting_system.bat
```

### Command Line
```bash
streamlit run betting_system_ui.py
```

Opens at: `http://localhost:8501`

---

## Features

### 🏠 Dashboard
- Week summary and key metrics
- Top 10 props preview
- Quick stats (total props, high confidence, OVER/UNDER counts)
- One-click navigation to all features

### 🎯 Prop Analysis
- View all analyzed props in sortable table
- Filter by:
  - Position (QB, RB, WR, TE)
  - Bet type (OVER, UNDER)
  - Minimum confidence
- Sort by:
  - Confidence score
  - Player name
  - Team
- Export filtered results

### 🎲 Parlay Builder
- Generate 2-5 leg parlays automatically
- Adjustable minimum confidence threshold
- View parlays organized by type
- See detailed leg breakdowns
- Confidence scores and risk levels
- Correlation analysis

### ✅ Validation
- Link to dedicated validation UI
- View validation statistics
- Track learned props
- Monitor validation rules

### 📊 Performance
- View recent parlay results
- Track win/loss records
- Agent calibration data
- Historical performance

### ⚙️ Settings
- Configure data paths
- Set default confidence levels
- Manage validation data
- System information

---

## UI Layout

```
┌─────────────────────────────────────────────────────┐
│  Sidebar              │  Main Content               │
├───────────────────────┼─────────────────────────────┤
│  🏈 NFL Betting       │  [Page Content]             │
│                       │                             │
│  Week: [12]           │  Dashboard / Props /        │
│  [📊 Load Data]       │  Parlays / Validation /     │
│                       │  Performance / Settings     │
│  ──────────────       │                             │
│  Navigation:          │                             │
│  ○ 🏠 Dashboard       │                             │
│  ○ 🎯 Prop Analysis   │                             │
│  ○ 🎲 Parlay Builder  │                             │
│  ○ ✅ Validation      │                             │
│  ○ 📊 Performance     │                             │
│  ○ ⚙️ Settings        │                             │
│                       │                             │
│  Status:              │                             │
│  ✅ Week 12 loaded    │                             │
│  1177 props analyzed  │                             │
└───────────────────────┴─────────────────────────────┘
```

---

## Workflow

### 1. Load Data
1. Select week in sidebar
2. Click "📊 Load Data"
3. Wait for analysis to complete
4. Green checkmark appears when ready

### 2. Explore Props
1. Go to "🎯 Prop Analysis"
2. Apply filters (position, bet type, confidence)
3. Sort by preferred criteria
4. Review props in table view

### 3. Generate Parlays
1. Go to "🎲 Parlay Builder"
2. Set minimum confidence
3. Click "Generate Parlays"
4. Review generated parlays by type

### 4. Validate (Optional)
1. Go to "✅ Validation"
2. Click link to open validation UI
3. Validate each parlay
4. System learns prop availability

### 5. Track Performance
1. Go to "📊 Performance"
2. View recent parlays
3. Check calibration data
4. Monitor success rates

---

## Pages Overview

### 🏠 Dashboard
**Purpose:** Quick overview and navigation hub

**What you see:**
- Total props, high confidence count
- OVER/UNDER distribution
- Top 10 props with confidence scores
- Quick access to features

**Use when:** Starting your analysis session

---

### 🎯 Prop Analysis
**Purpose:** Deep dive into individual props

**Features:**
- Filterable, sortable table
- Full prop details (player, team, opponent, line)
- Confidence scores
- Bet type indicators

**Use when:**
- Looking for specific props
- Researching particular players/teams
- Finding high-confidence opportunities

---

### 🎲 Parlay Builder
**Purpose:** Generate and review parlays

**Features:**
- One-click parlay generation
- Organized by leg count (2-5)
- Detailed leg breakdowns
- Confidence and risk ratings
- Correlation analysis

**Use when:**
- Ready to create betting combinations
- Comparing different parlay structures
- Reviewing parlay rationales

---

### ✅ Validation
**Purpose:** Verify DraftKings Pick6 availability

**Features:**
- Link to dedicated validation UI
- Validation statistics dashboard
- Rule and prop tracking

**Use when:**
- Before placing bets
- Teaching the system what's available
- Reviewing learned patterns

---

### 📊 Performance
**Purpose:** Track results and calibration

**Features:**
- Recent parlay history
- Win/loss tracking
- Agent calibration data
- Performance metrics

**Use when:**
- Reviewing past performance
- Checking calibration accuracy
- Analyzing long-term results

---

### ⚙️ Settings
**Purpose:** Configure system and manage data

**Features:**
- Path configuration
- Default values
- Data management
- System information

**Use when:**
- Customizing system behavior
- Clearing old data
- Checking system status

---

## Tips

### Efficient Workflow
1. **Load once per session** - Data persists while UI is running
2. **Use filters** - Narrow down props before analyzing
3. **Start with Dashboard** - Get overview before diving deep
4. **Validate early** - Run validation before betting day

### Navigation
- **Sidebar always visible** - Quick access to all pages
- **Week selector at top** - Change weeks anytime
- **Status indicator** - Shows if data is loaded

### Performance
- **First load is slow** (~10-30 seconds) - Analyzing all props
- **Page changes are instant** - Data already loaded
- **Filters are reactive** - Updates immediately

---

## Keyboard Shortcuts

Streamlit shortcuts:
- **R** - Rerun the app
- **C** - Clear cache
- **Ctrl+Shift+R** - Hard refresh

---

## Comparison: UI vs CLI

| Feature | CLI | UI |
|---------|-----|-----|
| **Learning Curve** | Commands to learn | ✅ Visual, intuitive |
| **Prop Browsing** | Scroll text | ✅ Sortable table |
| **Filtering** | Separate commands | ✅ Interactive filters |
| **Parlays** | Text output | ✅ Expandable cards |
| **Navigation** | Type commands | ✅ Click buttons |
| **Validation** | Type A/R/S | ✅ Checkboxes |
| **Multi-tasking** | Sequential | ✅ Keep browser open |
| **Visual Feedback** | Text only | ✅ Colors, metrics |

**Recommendation:** Use UI for regular workflow, CLI for automation/scripting

---

## Integration

### Works With
- ✅ CLI tools (shares same database)
- ✅ Validation UI (`validation_ui.py`)
- ✅ Existing Python scripts
- ✅ All betting analysis features

### Data Sharing
- Same `bets.db` database
- Same prop analysis engine
- Same validation system
- Seamless switching between UI/CLI

---

## Advanced Usage

### Custom Port
```bash
streamlit run betting_system_ui.py --server.port 8502
```

### Network Access
```bash
streamlit run betting_system_ui.py --server.address 0.0.0.0
```

### Headless Mode
```bash
streamlit run betting_system_ui.py --server.headless true
```

---

## Troubleshooting

### UI Won't Start
```bash
pip install streamlit pandas
streamlit run betting_system_ui.py
```

### Data Won't Load
- Check `data/` folder for CSV files
- Ensure week has betting lines
- Try different week

### Slow Performance
- First load takes time (normal)
- Close other browser tabs
- Restart UI if sluggish

### Changes Not Showing
- Press **R** to rerun
- Hard refresh: **Ctrl+Shift+R**
- Clear cache and rerun

---

## What's Next

After using the UI:
1. **Export validated parlays** - For betting platforms
2. **Track results** - Use performance page
3. **Refine system** - Add custom validation rules
4. **Iterate** - Each week improves accuracy

---

## Documentation

- **This file** - Main UI guide
- **`docs/VALIDATION_UI_GUIDE.md`** - Validation-specific docs
- **`HOW_TO_USE_VALIDATION.md`** - Validation workflow
- **`docs/PROP_VALIDATION_GUIDE.md`** - Complete validation reference

---

## Feedback

UI is actively developed. Features to potentially add:
- Live odds integration
- Prop comparison view
- Custom parlay builder (drag & drop)
- Export to CSV/PDF
- Mobile-responsive design

---

## Quick Reference

**Start UI:**
```
run_betting_system.bat
```

**Load Data:**
1. Select week
2. Click "Load Data"

**Find Props:**
1. Go to Prop Analysis
2. Filter & sort
3. Review table

**Build Parlays:**
1. Go to Parlay Builder
2. Set confidence
3. Generate

**Validate:**
1. Go to Validation
2. Open validation UI
3. Validate each parlay

**Stop UI:**
Press **Ctrl+C** in terminal

---

You're all set! Open `run_betting_system.bat` and start analyzing!
