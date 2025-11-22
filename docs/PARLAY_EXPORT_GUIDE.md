# Weekly Parlay Export for Calibration - User Guide

## Overview

The Weekly Parlay Export feature allows you to export all parlays generated for a specific week to a CSV file. This file can be manually filled with Win/Loss results and used for agent recalibration, implementing the "mark everything" philosophy to maximize learning data.

## Quick Start

### Export a Single Week

```bash
# Export parlays for week 12
python scripts/export_parlays_cli.py --week 12

# Export with specific year
python scripts/export_parlays_cli.py --week 12 --year 2024
```

### Export All Weeks

```bash
# Export all weeks that have parlays
python scripts/export_parlays_cli.py --all
```

### Preview Before Exporting

```bash
# Preview what will be exported (doesn't save file)
python scripts/export_parlays_cli.py --week 12 --preview
```

### List Available Weeks

```bash
# See which weeks have parlays available
python scripts/export_parlays_cli.py --list-weeks
```

## What Gets Exported

### Scope
- **ALL parlays** generated for the week (not just the ones bet on)
- **Both system-generated** (traditional/enhanced) and **custom** parlays
- **Individual legs**: One row per prop (6-leg parlay = 6 CSV rows)
- **All agent scores** for each prop
- **Confidence data**: Raw, correlation-adjusted, and final confidence

### File Format

**File naming**: `week_12_2024_parlays.csv`
**Location**: `data/calibration/`

### CSV Columns

| Column | Description | Example |
|--------|-------------|---------|
| week | Week number | 12 |
| year | Season year | 2024 |
| parlay_id | Unique parlay identifier | CUST_W12_a7f3e2d1_v1 |
| leg_number | Leg position in parlay | 1, 2, 3... |
| parlay_type | Type of parlay | traditional, enhanced, custom |
| was_bet_on | Whether this parlay was bet | TRUE / FALSE |
| player_name | Player full name | Josh Allen |
| position | Player position | QB |
| team | Player's team | BUF |
| opponent | Opposing team | KC |
| home_away | Home or away game | HOME / AWAY / UNKNOWN |
| prop_type | Type of prop | Pass Yards |
| line | Line value | 267.5 |
| prediction | Over or under | OVER / UNDER |
| leg_confidence | Individual leg confidence | 73.2 |
| parlay_raw_confidence | Pre-correlation confidence | 71.5 |
| correlation_adjustment | Correlation penalty | -2.0 |
| parlay_adjusted_confidence | Post-correlation confidence | 69.5 |
| dvoa_score | DVOA agent score (0-10) | 8.5 |
| matchup_score | Matchup agent score | 7.2 |
| volume_score | Volume agent score | 9.1 |
| injury_score | Injury agent score | 5.0 |
| trend_score | Trend agent score | 7.8 |
| gamescript_score | GameScript agent score | 8.3 |
| variance_score | Variance agent score | 6.5 |
| weather_score | Weather agent score | 10.0 |
| **bet_result** | **W or L (YOU FILL THIS)** | **(empty)** |

## Complete Workflow

### Step 1: Run Weekly Analysis
```bash
# Generate parlays for the week
python scripts/run_analysis.py --week 12
```

This creates parlays and saves them to `parlay_tracking.json`.

### Step 2: Place Bets

Mark which parlays you actually bet on:

```python
from scripts.analysis import ParlayTracker

tracker = ParlayTracker()
tracker.mark_bet("TRAD_W12_abc123_v1", bet_amount=10.0)
```

### Step 3: Export After Week Ends

```bash
# Export the week's parlays
python scripts/export_parlays_cli.py --week 12
```

Output:
```
================================================================================
📊 EXPORTING PARLAYS FOR WEEK 12 (2024)
================================================================================

Loading week 12 parlays from tracking system...
Found 15 total parlays:
  - 10 system parlays
  - 5 custom parlays
  - 8 parlays actually bet on

Converting parlays to individual legs...
✓ Converted 15 parlays into 90 individual legs

================================================================================
✅ EXPORT SUCCESSFUL
================================================================================
File: data/calibration/week_12_2024_parlays.csv
Total parlays: 15
Total legs exported: 90
Columns: 27

📝 Next steps:
  1. Open the CSV file in Excel/Google Sheets
  2. Fill in the 'bet_result' column with W (win) or L (loss) for each leg
  3. Save the file
  4. Run calibration analysis to adjust agent weights
================================================================================
```

### Step 4: Fill in Results

Open `week_12_2024_parlays.csv` in Excel:

1. Check game results for each prop
2. In the `bet_result` column:
   - Enter `W` if the leg hit (prop went OVER/UNDER as predicted)
   - Enter `L` if the leg missed
3. Save the file

Example:
```
player_name | prop_type  | line  | prediction | bet_result
Josh Allen  | Pass Yards | 267.5 | OVER       | W          ← He threw 285 yards
CMC         | Rush Yards | 95.5  | OVER       | L          ← He only got 78 yards
Jefferson   | Rec Yards  | 88.5  | OVER       | W          ← He had 112 yards
```

### Step 5: Run Calibration Analysis

(Future feature - will read these files to adjust agent weights)

```bash
# Analyze all completed weeks and suggest weight adjustments
python scripts/calibrate_agents.py
```

## Python API

You can also use the export functions programmatically:

```python
from scripts.analysis import export_weekly_parlays, export_all_parlays

# Export single week
filepath = export_weekly_parlays(week=12, year=2024)

# Export all weeks
filepaths = export_all_parlays(year=2024, overwrite=True)

# Preview without saving
from scripts.analysis import preview_weekly_parlays
preview_weekly_parlays(week=12)
```

## Advanced Usage

### Overwrite Without Prompting

```bash
# Useful for scripts/automation
python scripts/export_parlays_cli.py --week 12 --overwrite
```

### Export Multiple Weeks

```bash
# Loop through weeks 10-15
for week in {10..15}; do
  python scripts/export_parlays_cli.py --week $week --overwrite
done
```

### Check Available Weeks First

```bash
# See what's available
python scripts/export_parlays_cli.py --list-weeks

# Output:
# ================================================================================
# 📅 AVAILABLE WEEKS FOR 2024
# ================================================================================
# Weeks with parlays: 10, 11, 12, 13
# Total weeks: 4
# ================================================================================
```

## Data Details

### Agent Score Scale

All agent scores are exported on a **0-10 scale**:
- 0-3: Low confidence / negative signal
- 4-6: Neutral / moderate signal
- 7-10: High confidence / strong signal

The system handles conversion from the internal 0-100 scale automatically.

### Correlation Adjustment

- **Positive values** (+2 to +5): Bonus for beneficial correlations (same-game stacking)
- **Negative values** (-2 to -5): Penalty for risky correlations (same player, QB+WR stacking)
- **Zero**: No significant correlation detected

### Parlay Types

- **traditional**: Basic system-generated parlays
- **enhanced**: Correlation-optimized system parlays
- **custom**: User-built parlays from Custom Parlay Builder

## Troubleshooting

### No Parlays Found

```
❌ No parlays found for week 12 (2024)
   Make sure you've run analysis for this week first.
```

**Solution**: Run the analysis first:
```bash
python scripts/run_analysis.py --week 12
```

### File Already Exists

```
⚠️  File already exists: data/calibration/week_12_2024_parlays.csv
Overwrite? (y/n):
```

**Options**:
- Enter `y` to overwrite
- Enter `n` to cancel
- Use `--overwrite` flag to skip prompt

### Missing Agent Scores

If some agent scores are 0, it means:
- Agent didn't run for that prop (missing data)
- Agent returned None (insufficient data)
- Prop was added before that agent existed

This is normal and the calibration system handles it.

### Empty bet_result Column

This is **by design**! The CSV exports with an empty `bet_result` column for you to manually fill in after games complete.

## File Management

### Storage Location

```
data/
└── calibration/
    ├── week_10_2024_parlays.csv
    ├── week_11_2024_parlays.csv
    ├── week_12_2024_parlays.csv
    └── ...
```

The `data/calibration/` directory is automatically created if it doesn't exist.

### Backup Before Editing

Before filling in results, consider backing up the original export:

```bash
cp data/calibration/week_12_2024_parlays.csv data/calibration/week_12_2024_parlays_backup.csv
```

## Best Practices

1. **Export After Games Complete**
   Wait until all games for the week finish before exporting, so you can immediately fill in results.

2. **Fill Results Same Day**
   Fill in the `bet_result` column while results are fresh in your mind.

3. **Track Everything**
   Export ALL weeks, even if you didn't bet on most parlays. More data = better calibration.

4. **Double Check Results**
   Verify each W/L against official game stats to ensure accuracy.

5. **Version Control**
   Consider committing completed CSV files to git for history tracking.

## Future Enhancements

Planned features:
- [ ] Automatic result filling from ESPN/NFL API
- [ ] Agent calibration script that reads completed CSVs
- [ ] Visualization of agent performance over time
- [ ] Bulk import/export for multiple seasons
- [ ] Integration with DraftKings bet history

## Support

For issues or questions:
- Check this guide first
- Review `scripts/analysis/export_parlays.py` source code
- Create GitHub issue with "export" label

## Related Documentation

- [Custom Parlay Builder](CUSTOM_PARLAY_BUILDER.md)
- [Parlay Tracking System](../scripts/analysis/parlay_tracker.py)
- [Agent Calibration](../scripts/analysis/agent_calibrator.py)
