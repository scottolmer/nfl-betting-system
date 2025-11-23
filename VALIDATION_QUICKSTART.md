# Prop Validation Quick Start

## The Problem

You're generating parlays that include props **not available on DraftKings Pick6**. For example:
- ❌ Same player: UNDER completions + UNDER receptions
- ❌ Same player: UNDER passing yards + UNDER completions
- ❌ Other platform-specific restrictions

## The Solution

A hybrid validation system that:
1. ✅ **Auto-filters** using rules for known invalid combinations
2. ✅ **Lets you manually validate** each parlay
3. ✅ **Learns** which props work and which don't
4. ✅ **Rebuilds parlays** using only validated props

---

## Quick Start (3 Steps)

### Step 1: Run Your Analysis (As Usual)

```bash
# Your normal workflow - analyze props and build parlays
python betting_cli.py --week 12
```

### Step 2: Validate Parlays

```bash
# Run the complete validation workflow
python scripts/validation_integration_example.py --mode full --week 12
```

This will:
- Show you each parlay
- Ask you to Accept (A) or Reject (R) each one
- For rejected ones, ask which props are unavailable
- Rebuild parlays using valid props
- Give you final, DK Pick6-ready parlays

### Step 3: Use Final Parlays

The validated parlays are displayed and optionally saved to your database.

---

## Example Session

```
📊 2-LEG (Confidence: 68)
--------------------------------------------------------------------------------
  1. Josh Allen (BUF) - Pass Yds OVER 275.5
     Confidence: 70 | vs MIA
  2. Tyreek Hill (MIA) - Rec Yds OVER 85.5
     Confidence: 66 | vs BUF

  👉 Accept/Reject/Skip? (A/R/S): A
  ✅ Parlay accepted
```

If you reject:
```
  👉 Accept/Reject/Skip? (A/R/S): R
  Which props are NOT available? (e.g., '1,3'): 2
  ❌ Marked as unavailable: Tyreek Hill Rec Yds OVER
```

---

## What Gets Saved

The system remembers:
- ✅ Props marked as **available** (can use in future parlays)
- ❌ Props marked as **unavailable** (won't use again)
- 📋 **Validation rules** (auto-filter next time)

Next week, it'll auto-filter based on what you've learned!

---

## Files Created

| File | Purpose |
|------|---------|
| `scripts/analysis/prop_availability_validator.py` | Rule-based validation engine |
| `scripts/analysis/parlay_validator_interface.py` | Interactive validation CLI |
| `scripts/analysis/parlay_rebuilder.py` | Rebuilds parlays with valid props |
| `scripts/parlay_validation_cli.py` | Main CLI tool |
| `scripts/validation_integration_example.py` | Integration examples |
| `docs/PROP_VALIDATION_GUIDE.md` | Complete documentation |

---

## Common Tasks

### Add a Custom Rule

```bash
python scripts/parlay_validation_cli.py --mode add-rule
```

### Check Validation Stats

```bash
python scripts/parlay_validation_cli.py --mode stats
```

Output:
```
📊 VALIDATION SYSTEM STATISTICS
Total validation rules: 4
Props marked available: 127
Props marked unavailable: 23
```

### Integrate Into Your Code

```python
from scripts.parlay_validation_cli import validate_and_rebuild_workflow

# After building parlays
results = validate_and_rebuild_workflow(
    parlays=parlays,
    all_props=analyzed_props
)

final_parlays = results['final_parlays']
```

---

## Default Validation Rules

The system automatically filters these invalid combinations:

1. Same player: UNDER completions + UNDER receptions
2. Same player: UNDER passing yards + UNDER completions
3. Same player: UNDER rushing yards + UNDER rushing attempts
4. Same player: UNDER receiving yards + UNDER receptions

You can add more as you discover them!

---

## Tips

- **First time?** Just accept/reject honestly. The system learns.
- **Found a pattern?** Add it as a rule so it auto-filters next time.
- **Made a mistake?** You can manually edit the database or add inverse rules.
- **Weekly routine**: Validate new parlays every week before betting.

---

## Full Documentation

See `docs/PROP_VALIDATION_GUIDE.md` for:
- Complete API reference
- Advanced usage
- Database schema
- Troubleshooting
- Integration examples

---

## Support

Issues or questions? Check:
1. `docs/PROP_VALIDATION_GUIDE.md` - Full documentation
2. `scripts/validation_integration_example.py` - Working examples
3. Database: `bets.db` tables: `prop_validation_rules`, `prop_availability`
