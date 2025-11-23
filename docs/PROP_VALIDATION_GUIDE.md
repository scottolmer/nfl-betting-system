# Prop Validation & Parlay Rebuilding System

## Overview

This system solves the problem of **props that look good analytically but aren't actually available on DraftKings Pick6**.

Common issues:
- Same player UNDER completions + UNDER receptions (not allowed)
- Same player UNDER passing yards + UNDER completions (not allowed)
- Platform-specific restrictions that vary by prop

The system uses a **hybrid approach**:
1. **Rule-based filtering** - Automated rules for known invalid combinations
2. **Manual validation** - Interactive review of generated parlays
3. **Learning system** - Remembers which props work and which don't
4. **Automatic rebuild** - Creates new parlays using only validated props

---

## Components

### 1. `PropAvailabilityValidator`
Location: `scripts/analysis/prop_availability_validator.py`

**Purpose**: Validates props against rules and learned patterns

**Key Features**:
- Stores validation rules in database
- Default rules for common invalid combinations
- Checks parlays before they're finalized
- Learns from manual validations

**Database Tables**:
- `prop_validation_rules` - Rules for invalid prop combinations
- `prop_availability` - Individual props marked as available/unavailable
- `parlay_validation_history` - History of validated parlays

### 2. `ParlayValidatorInterface`
Location: `scripts/analysis/parlay_validator_interface.py`

**Purpose**: Interactive CLI for manual validation

**Workflow**:
1. Displays generated parlays
2. Pre-filters using validation rules
3. Prompts user to Accept/Reject/Skip each parlay
4. For rejected parlays, asks which specific props are unavailable
5. Saves validation decisions to database

### 3. `ParlayRebuilder`
Location: `scripts/analysis/parlay_rebuilder.py`

**Purpose**: Rebuilds parlays using validated props

**Features**:
- Extracts valid props from rejected parlays
- Combines with other available props
- Rebuilds parlays with same structure (2-leg, 3-leg, etc.)
- Respects player diversity rules
- Validates new parlays against rules before finalizing

### 4. Integration Scripts
- `scripts/parlay_validation_cli.py` - Standalone CLI tool
- `scripts/validation_integration_example.py` - Integration examples

---

## Quick Start

### Method 1: Full Workflow (Recommended)

Run the complete workflow from data loading to validated parlays:

```bash
python scripts/validation_integration_example.py --mode full --week 12
```

This will:
1. Load props for the week
2. Run agent analysis
3. Build parlays
4. **Validate parlays interactively**
5. **Rebuild using valid props**
6. Save final parlays

### Method 2: Integrate into Existing Code

Add validation to your existing parlay generation:

```python
from scripts.parlay_validation_cli import validate_and_rebuild_workflow

# After building parlays (your existing code)
parlays = builder.build_parlays(analyzed_props)

# Add validation step
results = validate_and_rebuild_workflow(
    parlays=parlays,
    all_props=analyzed_props,
    db_path="bets.db"
)

# Use final validated parlays
final_parlays = results['final_parlays']
```

---

## Interactive Validation Workflow

When you run validation, you'll see:

```
🔍 PARLAY VALIDATION - DraftKings Pick6 Availability Check
================================================================================

📋 Pre-filtering with validation rules...

❌ 2-LEG Parlay #2 - RULE VIOLATIONS:
   ❌ Patrick Mahomes: Completions UNDER + Receptions UNDER (Same player: UNDER completions + UNDER receptions)

✅ 2-LEG Parlay #1 - Passed rule checks
✅ 3-LEG Parlay #1 - Passed rule checks

🎯 INTERACTIVE VALIDATION
================================================================================

Review parlays that passed rule checks:

--------------------------------------------------------------------------------
📊 2-LEG (Confidence: 68)
--------------------------------------------------------------------------------
  1. Josh Allen (BUF) - Pass Yds OVER 275.5
     Confidence: 70 | vs MIA
  2. Tyreek Hill (MIA) - Rec Yds OVER 85.5
     Confidence: 66 | vs BUF

  ✅ Diversified WR/QB across 2 games

  👉 Accept/Reject/Skip? (A/R/S): A
  ✅ Parlay accepted - all props marked as available
```

### Rejection Flow

If you reject a parlay:

```
  👉 Accept/Reject/Skip? (A/R/S): R

  Which props are NOT available? (comma-separated numbers, e.g., '1,3'):
  👉 Invalid props: 2

  ❌ Marked as unavailable: Tyreek Hill Rec Yds OVER
  ❌ Parlay rejected - props marked accordingly
```

The system will:
- Mark prop #2 as unavailable (never use again)
- Mark prop #1 as available (can use in rebuilds)
- Save this knowledge for future validations

---

## Validation Rules

### Default Rules

The system comes with default rules for common invalid combinations:

1. **Same Player UNDER Completions + Receptions**
   - QB/WR/TE correlation issue
   - Example: Can't bet UNDER on both Mahomes completions and Kelce receptions

2. **Same Player UNDER Passing Yards + Completions**
   - Highly correlated stats
   - Example: Can't bet UNDER on both passing yards and completions

3. **Same Player UNDER Rushing Yards + Attempts**
   - Directly correlated

4. **Same Player UNDER Receiving Yards + Receptions**
   - Tightly coupled stats

### Adding Custom Rules

Add new rules based on what you discover:

```python
from scripts.analysis.parlay_validator_interface import ParlayValidatorInterface

interface = ParlayValidatorInterface()

interface.validator.add_custom_rule(
    description="Same player: UNDER touchdowns + UNDER yards",
    rule_type="same_player_props",
    conditions={
        "player": "same",
        "prop_types": ["Pass TDs", "Pass Yds"],
        "bet_types": ["UNDER", "UNDER"]
    },
    auto_applied=True
)
```

Or use the interactive interface:

```bash
python scripts/parlay_validation_cli.py --mode add-rule
```

---

## Parlay Rebuilding

### How It Works

When parlays are rejected:

1. **Extract Valid Props**: Props marked as available are extracted from rejected parlays
2. **Pool Props**: Combine with all other available props
3. **Filter**: Remove props marked as unavailable
4. **Rebuild**: Generate new parlays using the same structure
5. **Validate**: Check new parlays against rules before finalizing

### Example

Original parlays:
- ✅ 2-leg parlay #1 (valid)
- ❌ 2-leg parlay #2 (invalid - 1 prop unavailable, 1 prop valid)
- ✅ 3-leg parlay #1 (valid)
- ❌ 3-leg parlay #2 (invalid - 2 props unavailable, 1 prop valid)

After rebuilding:
- 2-leg parlay #1 (original valid)
- **2-leg parlay #2 (rebuilt using 1 extracted prop + 1 new prop)**
- 3-leg parlay #1 (original valid)
- **3-leg parlay #2 (rebuilt using 1 extracted prop + 2 new props)**

Result: Full set of 10 parlays using only available props!

---

## Database Schema

### `prop_validation_rules`

Stores validation rules:

```sql
CREATE TABLE prop_validation_rules (
    rule_id TEXT PRIMARY KEY,
    description TEXT,
    rule_type TEXT,
    conditions TEXT,  -- JSON
    auto_applied INTEGER DEFAULT 1,
    created_date TEXT,
    times_triggered INTEGER DEFAULT 0
)
```

### `prop_availability`

Tracks individual prop availability:

```sql
CREATE TABLE prop_availability (
    prop_signature TEXT PRIMARY KEY,
    player_name TEXT,
    prop_type TEXT,
    bet_type TEXT,
    is_available INTEGER,
    last_validated TEXT,
    validation_source TEXT,
    notes TEXT
)
```

### `parlay_validation_history`

History of validation sessions:

```sql
CREATE TABLE parlay_validation_history (
    validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    parlay_signature TEXT,
    props_json TEXT,
    is_valid INTEGER,
    invalid_reason TEXT,
    validated_date TEXT,
    week INTEGER
)
```

---

## Validation Statistics

Check system statistics:

```bash
python scripts/parlay_validation_cli.py --mode stats
```

Output:
```
📊 VALIDATION SYSTEM STATISTICS
================================================================================
Total validation rules: 4
Props marked available: 127
Props marked unavailable: 23
================================================================================
```

---

## Advanced Usage

### Programmatic Validation

Validate a single parlay without user input:

```python
from scripts.analysis.parlay_validator_interface import ParlayValidatorInterface

interface = ParlayValidatorInterface()

is_valid, violations = interface.quick_validate_parlay(parlay)

if not is_valid:
    print(f"Parlay invalid: {violations}")
```

### Filter Props by Availability

Filter props before building parlays:

```python
from scripts.analysis.prop_availability_validator import PropAvailabilityValidator

validator = PropAvailabilityValidator()

# Only get props that haven't been marked as unavailable
available_props = validator.filter_available_props(all_analyzed_props)

# Build parlays using only available props
parlays = builder.build_parlays(available_props)
```

### Custom Rebuild Targets

Rebuild specific parlay counts:

```python
from scripts.analysis.parlay_rebuilder import ParlayRebuilder

rebuilder = ParlayRebuilder()

new_parlays = rebuilder.rebuild_parlays(
    valid_props_pool=valid_props,
    additional_props=all_props,
    target_counts={
        "2-leg": 5,  # Build 5 two-leg parlays
        "3-leg": 2,  # Build 2 three-leg parlays
        "4-leg": 1   # Build 1 four-leg parlay
    }
)
```

---

## Best Practices

1. **Validate Every Week**: Run validation on new parlays before betting
2. **Learn Over Time**: The more you validate, the smarter the system gets
3. **Add Rules Proactively**: If you discover new invalid combinations, add them as rules
4. **Review Stats Periodically**: Check what props are being filtered most often
5. **Keep Database**: Don't delete `bets.db` - it contains all learned validations

---

## Troubleshooting

### "No parlays found"

Make sure you've generated parlays first:
```python
builder = ParlayBuilder()
parlays = builder.build_parlays(analyzed_props)
```

### "Database not found"

The database is created automatically on first run. Make sure you're in the project root directory.

### "All parlays rejected"

Check validation stats to see what's being filtered:
```bash
python scripts/parlay_validation_cli.py --mode stats
```

You may need to:
- Lower min_confidence threshold
- Add more props to the pool
- Review validation rules (some might be too strict)

---

## Integration Checklist

- [ ] Run validation on generated parlays
- [ ] Review and accept/reject each parlay
- [ ] Rebuild using validated props
- [ ] Save final parlays to database
- [ ] Add custom rules as you discover them
- [ ] Check validation stats weekly
- [ ] Export final parlays for betting

---

## Future Enhancements

Possible improvements:
1. **Auto-learning**: Automatically detect patterns in rejected parlays
2. **Platform-specific rules**: Different rules for different betting platforms
3. **Bulk validation**: Validate multiple weeks at once
4. **Rule suggestions**: Suggest new rules based on rejection patterns
5. **Web interface**: Browser-based validation instead of CLI
