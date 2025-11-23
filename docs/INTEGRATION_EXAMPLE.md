# How to Use the Validation System

## Method 1: Standalone Command (Easiest)

Just run this after your normal analysis:

```bash
python scripts/validation_integration_example.py --mode full --week 12
```

This does **everything**: loads data, analyzes props, builds parlays, validates, rebuilds, and shows final results.

---

## Method 2: Add to betting_cli.py

You can add a new command to your existing CLI. Add this method to the `BettingAnalyzerCLI` class:

```python
def validate_parlays(self, week=None):
    """Validate and rebuild parlays interactively"""
    from scripts.parlay_validation_cli import validate_and_rebuild_workflow

    if week is None:
        week = self.week

    # Load and analyze props
    print(f"\n🔍 Loading data for week {week}...")
    context = self.loader.load_all_data(week=week)

    print(f"🤖 Analyzing props...")
    analyzed_props = self.analyzer.analyze_all_props(context, min_confidence=40)

    # Build parlays
    print(f"\n🎯 Building parlays...")
    parlays = self.parlay_builder.build_parlays(analyzed_props, min_confidence=58)

    # NEW: Validate and rebuild
    print(f"\n🔍 Starting validation workflow...")
    results = validate_and_rebuild_workflow(
        parlays=parlays,
        all_props=analyzed_props,
        db_path="bets.db"
    )

    # Show final parlays
    final_parlays = results['final_parlays']
    formatted = self.parlay_builder.format_parlays_for_betting(
        final_parlays,
        "DraftKings Pick6"
    )
    print(formatted)

    # Store for other commands
    self.last_parlays = final_parlays

    return results
```

Then add to the command handler (around line 400-500 where commands are processed):

```python
elif cmd == 'validate-parlays':
    self.validate_parlays()
```

And add to the help text (around line 54-88):

```python
print("  validate-parlays         - Validate parlays interactively")
```

Now you can use:
```bash
python betting_cli.py
>>> validate-parlays
```

---

## Method 3: After 'parlays' Command

Integrate validation directly after building parlays. Modify the `run_parlays()` method:

```python
def run_parlays(self, min_confidence=58):
    """Generate parlays, then optionally validate them"""
    # ... existing code to build parlays ...

    # After building parlays, ask if user wants to validate
    validate = input("\n🔍 Validate these parlays for DK Pick6 availability? (Y/N): ").strip().upper()

    if validate == 'Y':
        from scripts.parlay_validation_cli import validate_and_rebuild_workflow

        # Get all analyzed props
        context = self.loader.load_all_data(week=self.week)
        analyzed_props = self.analyzer.analyze_all_props(context, min_confidence=40)

        # Validate and rebuild
        results = validate_and_rebuild_workflow(
            parlays=parlays,
            all_props=analyzed_props
        )

        # Use validated parlays
        parlays = results['final_parlays']

        # Re-display final parlays
        formatted = self.parlay_builder.format_parlays_for_betting(parlays, "DraftKings Pick6")
        print(formatted)

    self.last_parlays = parlays
    return parlays
```

---

## What Happens During Validation

### Step 1: Pre-filtering
```
📋 Pre-filtering with validation rules...

✅ 2-LEG Parlay #1 - Passed rule checks
❌ 2-LEG Parlay #2 - RULE VIOLATIONS:
   ❌ Patrick Mahomes: Completions UNDER + Pass Yds UNDER
```

### Step 2: Interactive Review
```
📊 2-LEG (Confidence: 68)
--------------------------------------------------------------------------------
  1. Josh Allen (BUF) - Pass Yds OVER 275.5
     Confidence: 70 | vs MIA
  2. Stefon Diggs (BUF) - Rec Yds OVER 75.5
     Confidence: 66 | vs MIA

  ✅ Same-game WR/QB (BUF vs MIA)

  👉 Accept/Reject/Skip? (A/R/S):
```

**Your options:**
- **A (Accept)**: Both props are available on DK Pick6 → Keeps parlay, marks props as available
- **R (Reject)**: One or both props aren't available → System asks which ones
- **S (Skip)**: Don't validate this one right now

### Step 3: Rejection Flow
```
  👉 Accept/Reject/Skip? (A/R/S): R

  Which props are NOT available? (comma-separated numbers, e.g., '1,3'):
  👉 Invalid props: 2

  ❌ Marked as unavailable: Stefon Diggs Rec Yds OVER
  ✅ Marked as available: Josh Allen Pass Yds OVER
```

### Step 4: Rebuild
```
🔨 REBUILDING PARLAYS
   📦 Total unique props: 150
   ✅ Eligible props (conf 58+): 87
   🎯 Target parlays: 10

  🔨 Building 3x 2-leg parlays...
    ✅ Built 2-leg parlay #1 (Conf: 69)
    ✅ Built 2-leg parlay #2 (Conf: 67)
```

### Step 5: Final Output
```
✅ WORKFLOW COMPLETE
================================================================================
  2-leg: 3 parlays (was 3)
  3-leg: 3 parlays (was 3)
  4-leg: 3 parlays (was 3)
  5-leg: 1 parlay (was 1)
```

---

## Quick Commands Reference

### Check validation stats
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
```

### Add a custom rule
```bash
python scripts/parlay_validation_cli.py --mode add-rule
```

---

## Real-World Example

Let's say you run your normal workflow:

```bash
python betting_cli.py
>>> week 12
>>> parlays
```

You get 10 parlays but you know some props might not be on DK Pick6. Now run:

```bash
python scripts/validation_integration_example.py --mode full --week 12
```

**What happens:**
1. System shows you each parlay
2. You check DK Pick6 app/website
3. For each parlay:
   - If all props are there → Type **A**
   - If some props missing → Type **R** and specify which ones
   - If unsure → Type **S** to skip

4. System remembers your answers
5. Rebuilds parlays using only validated props
6. Shows final 10 parlays, all DK Pick6-ready!

**Next week:**
- Many parlays auto-filtered by rules
- Only validate new combinations
- System gets smarter each week

---

## Troubleshooting

### "No module named 'scripts.parlay_validation_cli'"

Make sure you're in the project root directory:
```bash
cd C:\Users\scott\Desktop\nfl-betting-systemv2
python scripts/validation_integration_example.py --mode full --week 12
```

### "No props found for week X"

Load betting lines first:
```bash
python betting_cli.py
>>> pull-lines
>>> exit
python scripts/validation_integration_example.py --mode full --week 12
```

### "All parlays rejected"

This means most props aren't available. You might need to:
1. Lower confidence threshold: `--min-confidence 55`
2. Check that you have recent betting lines
3. Review validation rules (they might be too strict)

---

## Summary

**Easiest way:**
```bash
python scripts/validation_integration_example.py --mode full --week 12
```

**After each validation session:**
- System learns which props work
- Future weeks require less manual validation
- Auto-filtering gets better over time

**Result:**
- 10 parlays guaranteed to be available on DK Pick6
- No wasted time building parlays you can't actually place
- System learns your platform's rules automatically
