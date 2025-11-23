# How to Use the Validation System - Quick Guide

## ✅ System is Ready!

All tests passed. The validation system is installed and working.

---

## Quick Start (2 Commands)

### 1. Run Validation Workflow
```bash
python scripts/validation_integration_example.py --mode full --week 12
```

This will:
- Load week 12 data
- Analyze props
- Build 10 parlays
- **Start interactive validation**

### 2. Answer Questions

When it shows each parlay, you'll see something like:

```
📊 2-LEG (Confidence: 71)
--------------------------------------------------------------------------------
  1. Kyler Murray (ARI) - Pass Yds OVER 225.5
     Confidence: 72 | vs SEA
  2. Marvin Harrison Jr. (ARI) - Rec Yds OVER 65.5
     Confidence: 70 | vs SEA

  ✅ Same-game WR/QB (ARI vs SEA)

  👉 Accept/Reject/Skip? (A/R/S):
```

**Check DraftKings Pick6 app/website and type:**
- **A** - Both props are available → Keeps parlay
- **R** - One or both props aren't available → System asks which
- **S** - Skip for now

---

## What Happens After You Respond

### If You Accept (A):
- ✅ Parlay is kept
- ✅ Both props marked as "available"
- System can reuse these props

### If You Reject (R):
```
  Which props are NOT available? (comma-separated numbers, e.g., '1,3'):
  👉 Invalid props: 2
```

- ❌ Prop #2 marked as "unavailable" (won't use again)
- ✅ Prop #1 marked as "available" (can reuse)
- System rebuilds this parlay later

---

## After All Parlays Reviewed

The system will:

1. **Show Summary**
   ```
   ✅ Valid parlays: 7
   ❌ Invalid parlays: 3
   📦 Valid props pool: 95 props
   ```

2. **Ask to Rebuild**
   ```
   🔨 Rebuild parlays using validated props? (Y/N):
   ```

3. **Rebuild Parlays** (if you say Y)
   - Extracts valid props from rejected parlays
   - Combines with other available props
   - Builds new parlays (same structure: 2-leg, 3-leg, etc.)
   - Validates new parlays against rules

4. **Show Final 10 Parlays**
   - All guaranteed to be DK Pick6-ready
   - Formatted and ready to bet

---

## Example Session

```bash
PS C:\users\scott\desktop\nfl-betting-systemv2> python scripts/validation_integration_example.py --mode full --week 12

================================================================================
📊 WEEK 12 PARLAY GENERATION WITH VALIDATION
================================================================================

🔍 STEP 1: Loading data and analyzing props...
   ✅ Loaded data for week 12

🤖 STEP 2: Running agent analysis...
   ✅ Analyzed 1177 props

🎯 STEP 3: Building initial parlays...
   ✅ Built 10 parlays

================================================================================
🔍 STEP 4: VALIDATION & REBUILD WORKFLOW
================================================================================

📋 Pre-filtering with validation rules...

✅ 2-LEG Parlay #1 - Passed rule checks
✅ 2-LEG Parlay #2 - Passed rule checks
❌ 2-LEG Parlay #3 - RULE VIOLATIONS:
   ❌ Patrick Mahomes: Completions UNDER + Pass Yds UNDER

🎯 INTERACTIVE VALIDATION
================================================================================

📊 2-LEG (Confidence: 71)
--------------------------------------------------------------------------------
  1. Kyler Murray (ARI) - Pass Yds OVER 225.5
  2. Marvin Harrison Jr. (ARI) - Rec Yds OVER 65.5

  👉 Accept/Reject/Skip? (A/R/S): A    <-- YOU TYPE THIS
  ✅ Parlay accepted - all props marked as available

[... continues for each parlay ...]

📊 VALIDATION SUMMARY
================================================================================
✅ Valid parlays: 7
❌ Invalid parlays: 3
📦 Valid props pool: 95 props

🔨 Rebuild parlays using validated props? (Y/N): Y    <-- YOU TYPE THIS

🔨 REBUILDING PARLAYS
   ✅ Built new 2-leg parlay (Conf: 69)
   ✅ Built new 3-leg parlay (Conf: 67)
   ✅ Built new 4-leg parlay (Conf: 65)

✅ WORKFLOW COMPLETE
================================================================================
  2-leg: 3 parlays (was 3)
  3-leg: 3 parlays (was 3)
  4-leg: 3 parlays (was 3)
  5-leg: 1 parlay (was 1)

[Shows final formatted parlays]

💾 Save these parlays to database? (Y/N):    <-- OPTIONAL
```

---

## Default Rules (Auto-Filters These)

The system automatically rejects parlays with these combinations:

1. ❌ Same player: UNDER completions + UNDER receptions
2. ❌ Same player: UNDER passing yards + UNDER completions
3. ❌ Same player: UNDER rushing yards + UNDER rushing attempts
4. ❌ Same player: UNDER receiving yards + UNDER receptions

These get filtered **before** you see them.

---

## Next Time You Run It

**Week 1**: Validate all 10 parlays manually

**Week 2**:
- Auto-filters 3 parlays (rules)
- You validate 7 parlays
- System remembers more props

**Week 3**:
- Auto-filters 4 parlays
- Auto-skips 2 (known bad props)
- You validate only 4 new ones

**The system gets smarter each week!**

---

## Other Commands

### Check Statistics
```bash
python scripts/parlay_validation_cli.py --mode stats
```

Shows:
- Total validation rules: 4
- Props marked available: 127
- Props marked unavailable: 23

### Add Custom Rule
```bash
python scripts/parlay_validation_cli.py --mode add-rule
```

Walks you through adding a new rule for invalid combinations you discover.

---

## Tips

1. **First time?** Be honest about availability. The system learns from you.

2. **Found a pattern?** Add it as a custom rule so it auto-filters next time.

3. **Made a mistake?** Run validation again - you can override previous decisions.

4. **Weekly routine**:
   ```bash
   python betting_cli.py
   >>> pull-lines
   >>> exit
   python scripts/validation_integration_example.py --mode full --week 12
   ```

5. **Database**: Don't delete `bets.db` - it stores all learned validations.

---

## Troubleshooting

**Error: "No data found"**
- Run `python betting_cli.py` first
- Use `pull-lines` to get betting lines
- Then run validation

**All parlays auto-rejected**
- Check stats: `python scripts/parlay_validation_cli.py --mode stats`
- Rules might be too strict
- Lower confidence: modify min_confidence in the code

**Want to start fresh?**
```bash
# This clears learned validations (keeps rules)
python -c "import sqlite3; conn = sqlite3.connect('bets.db'); conn.execute('DELETE FROM prop_availability'); conn.commit()"
```

---

## Documentation

- **This file**: Quick start guide
- **`VALIDATION_QUICKSTART.md`**: Reference guide
- **`docs/INTEGRATION_EXAMPLE.md`**: Code integration examples
- **`docs/PROP_VALIDATION_GUIDE.md`**: Complete documentation (450 lines)

---

## You're Ready!

Just run:
```bash
python scripts/validation_integration_example.py --mode full --week 12
```

And follow the prompts. The system will guide you through the rest!
