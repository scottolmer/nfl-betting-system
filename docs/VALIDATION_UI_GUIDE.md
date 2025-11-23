# Validation UI Guide

## Quick Start

### Option 1: Double-click (Windows)
```
run_validation_ui.bat
```

### Option 2: Command line
```bash
streamlit run validation_ui.py
```

The UI will open in your browser at `http://localhost:8501`

---

## UI Overview

```
┌─────────────────────────────────────────────────────┐
│  Sidebar                  │  Main Content           │
├───────────────────────────┼─────────────────────────┤
│  🏈 Parlay Validator      │  Parlay Display         │
│                           │                         │
│  Week: [12]               │  📊 2-LEG Parlay #1     │
│  [Load & Generate]        │  Confidence: 71%        │
│                           │                         │
│  ──────────────────       │  Props:                 │
│  📊 Statistics            │  1. Josh Allen          │
│  Total: 10                │     Pass Yds OVER 275.5 │
│  Validated: 3             │     [✓] Available       │
│  Remaining: 7             │                         │
│  [====>    ] 30%          │  2. Stefon Diggs        │
│                           │     Rec Yds OVER 75.5   │
│  ──────────────────       │     [✓] Available       │
│  System Stats:            │                         │
│  Rules: 4                 │  [✅ Accept] [❌ Mark] [⏭️ Skip]
│  Available: 127           │                         │
│  Unavailable: 23          │                         │
└───────────────────────────┴─────────────────────────┘
```

---

## How to Use

### Step 1: Load Data
1. Select **Week** in the sidebar (e.g., 12)
2. Click **"📊 Load & Generate Parlays"**
3. Wait for props to load and parlays to generate

### Step 2: Validate Parlays
For each parlay shown:

1. **Check DraftKings Pick6** - Open the app/website
2. **Mark availability**:
   - Leave checkboxes ✓ if props are available
   - Uncheck ☐ if props are NOT available
3. **Choose action**:
   - **✅ Accept All** - All props available (keeps parlay)
   - **❌ Mark Invalid Props** - Some props unavailable (unchecked ones)
   - **⏭️ Skip** - Skip this parlay for now

### Step 3: Review & Rebuild
After validating all parlays:

1. **Review summary** - See valid/invalid counts
2. **Click "🔨 Rebuild Parlays"** - System creates new parlays with valid props
3. **Click "📊 View Final Parlays"** - See formatted output

---

## Features

### Visual Feedback
- **Progress bar** - Shows validation progress
- **Statistics** - Real-time counts (validated, remaining, learned)
- **Color coding** - Green for valid, red for invalid
- **Confidence scores** - Easy to see at a glance

### Smart Validation
- **Auto-filtering** - Rules violations automatically rejected
- **Learning system** - Remembers prop availability
- **Props tracking** - Shows which props are known available/unavailable

### Interactive Controls
- **Checkboxes** - Toggle individual prop availability
- **Buttons** - Clear actions (Accept, Mark, Skip)
- **Navigation** - Auto-advances to next parlay

---

## Example Session

1. **Start UI**
   ```bash
   run_validation_ui.bat
   ```

2. **Load Week 12**
   - Select week: 12
   - Click "Load & Generate Parlays"
   - Wait ~10-30 seconds

3. **First Parlay Appears**
   ```
   📊 2-LEG Parlay #1
   Confidence: 71%

   Props:
   1. Josh Allen - Pass Yds OVER 275.5
      [✓] Available
   2. Stefon Diggs - Rec Yds OVER 75.5
      [✓] Available

   [✅ Accept All] [❌ Mark Invalid] [⏭️ Skip]
   ```

4. **Check DK Pick6**
   - Open DraftKings Pick6 app
   - Search for these props
   - Both available ✓

5. **Click "✅ Accept All"**
   - Props marked as available
   - Next parlay loads automatically

6. **Continue Until Complete**
   - Progress bar shows 10%, 20%, 30%...
   - Statistics update in real-time

7. **All Done**
   ```
   ✅ All parlays validated!

   📊 Validation Summary
   ✅ Valid: 7
   ❌ Invalid: 3
   📦 Props Learned: 150

   [🔨 Rebuild Parlays] [📊 View Final Parlays]
   ```

8. **Rebuild & Export**
   - Click "Rebuild Parlays"
   - System creates 3 new parlays using valid props
   - View final 10 parlays ready for betting

---

## Tips

### Efficient Validation
1. **Open DK Pick6 first** - Have it ready in another window
2. **Use keyboard** - Space to toggle checkboxes, Tab to navigate
3. **Be honest** - System learns from your feedback

### Understanding Checkboxes
- **✓ Checked** = Prop is available on DK Pick6
- **☐ Unchecked** = Prop is NOT available
- **Default: All checked** - Assume available unless you know otherwise

### Quick Actions
- **All available?** → Click "✅ Accept All"
- **One unavailable?** → Uncheck it, then "❌ Mark Invalid"
- **Multiple unavailable?** → Uncheck all, then "❌ Mark Invalid"
- **Not sure?** → Click "⏭️ Skip"

### Progress Tracking
- **Progress bar** - Visual percentage
- **Statistics** - Exact counts
- **Remaining counter** - How many left

---

## Keyboard Shortcuts

Streamlit provides these shortcuts:
- **R** - Rerun the app
- **C** - Clear cache
- **Ctrl+C** (in terminal) - Stop the app

---

## Troubleshooting

### UI won't start
```bash
# Install streamlit if needed
pip install streamlit

# Then run
streamlit run validation_ui.py
```

### "No parlays generated"
- Check that betting lines CSV exists for that week
- Try lowering confidence threshold (modify code: `min_confidence=50`)

### Changes not saving
- Database: `bets.db` stores all validations
- Don't delete this file
- Validations persist across sessions

### Browser shows old data
- Press **R** to rerun
- Or click "Always rerun" in the top-right menu

### Want to start fresh
Click "Load & Generate Parlays" again - resets validation state for that session

---

## Advantages Over CLI

| Feature | CLI | UI |
|---------|-----|-----|
| Visual feedback | Text only | ✓ Progress bars, colors |
| Ease of use | Type A/R/S | ✓ Click buttons |
| Prop toggling | Type numbers | ✓ Individual checkboxes |
| Progress tracking | Manual count | ✓ Automatic |
| Multi-tasking | Sequential | ✓ Keep DK Pick6 open |
| Statistics | Text dump | ✓ Live dashboard |

---

## Next Steps

After validation:
1. **View Final Parlays** - Copy to clipboard
2. **Save to database** - Already done automatically
3. **Export** - Use existing export tools if needed
4. **Place bets** - Use final validated parlays on DK Pick6

---

## Integration with Existing System

The UI uses your existing backend:
- ✅ Same `PropAvailabilityValidator`
- ✅ Same database (`bets.db`)
- ✅ Same validation rules
- ✅ Same learning system

You can switch between UI and CLI anytime - they share the same data!

---

## Advanced Usage

### Run on Different Port
```bash
streamlit run validation_ui.py --server.port 8502
```

### Run Without Browser Opening
```bash
streamlit run validation_ui.py --server.headless true
```

### Share with Others
```bash
# Make accessible on network
streamlit run validation_ui.py --server.address 0.0.0.0
```

---

## Screenshots Reference

### Sidebar
- Week selector (number input)
- Load button (primary blue)
- Statistics card (metrics)
- Progress bar (animated)

### Main Content
- Parlay header (title + confidence)
- Props list (checkboxes)
- Action buttons (3 columns)
- Navigation footer

### After Completion
- Summary metrics (3 cards)
- Rebuild button (large, primary)
- View button (secondary)
- Final output (text box)

---

## Feedback & Issues

The UI is new! If you find any issues:
1. Note what you were doing
2. Check the terminal for error messages
3. Try restarting the UI
4. Fall back to CLI if needed: `python scripts/validation_integration_example.py`
