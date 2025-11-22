# Custom Parlay Builder - Quick Start Guide

## What It Does

Build custom 6-leg parlays from analyzed props when DraftKings lines don't match system parlays. Includes full correlation analysis and confidence scoring.

## Quick Usage

### Command Line (Recommended)

```bash
# Build a custom parlay for week 12
python scripts/run_custom_parlay_builder.py --week 12

# Preview available props first
python scripts/run_custom_parlay_builder.py --week 12 --preview
```

### Python API

```python
from scripts.analysis import run_custom_parlay_builder, NFLDataLoader, PropAnalyzer

# Load and analyze props
loader = NFLDataLoader()
context = loader.load_all_data(week=12)
analyzer = PropAnalyzer()
analyzed_props = analyzer.analyze_all_props(context)

# Run interactive builder
parlay_id = run_custom_parlay_builder(analyzed_props, week=12)
```

## Interactive Workflow

1. **View Props** - Browse all analyzed props sorted by confidence
2. **Select 6 Legs** - Choose via search, filter, or browse
   - Search by player name
   - Filter by position (QB, RB, WR, TE, K)
   - Filter by stat type (Pass Yds, Rush Yds, etc.)
3. **Analyze** - Auto-runs correlation analysis via Claude
4. **Save** - Saves to `parlay_tracking.json` with "custom" flag

## Key Features

✅ **No Duplicate Players** - System enforces 1 prop per player
✅ **Correlation Detection** - Claude analyzes dependencies
✅ **Confidence Adjustment** - Raw confidence adjusted for correlations
✅ **Agent Breakdown** - See which agents contributed to each prop
✅ **Full Tracking** - Integrates with existing parlay tracker

## After Creating a Parlay

### Mark as Bet
```python
from scripts.analysis import ParlayTracker

tracker = ParlayTracker()
tracker.mark_bet("CUST_W12_a7f3e2d1_v1", bet_amount=10.0)
```

### Log Results
```python
tracker.mark_result(
    parlay_id="CUST_W12_a7f3e2d1_v1",
    result="won",  # or "lost"
    actual_payout=410.0
)
```

### View Stats
```python
# Custom parlays only
stats = tracker.get_statistics(parlay_type="custom", bet_only=True)

# Export to CSV
tracker.export_to_csv("custom_parlays.csv")
```

## Example Output

```
📈 CORRELATION ANALYSIS RESULTS
═══════════════════════════════════════════════════════
Raw Confidence:        75.3%
Correlation Adjust:    -2.0
Adjusted Confidence:   73.3%
Recommendation:        ACCEPT

Reasoning: Minor correlation detected between KC QB and WR in same game.
          Slight downward adjustment applied.
═══════════════════════════════════════════════════════

✅ CUSTOM PARLAY SAVED SUCCESSFULLY
═══════════════════════════════════════════════════════
Parlay ID: CUST_W12_a7f3e2d1_v1
Week: 12
Type: CUSTOM
Raw Confidence: 75.3%
Adjusted Confidence: 73.3%
Recommended Kelly Bet: 2.33 units
Payout Odds: +4000
═══════════════════════════════════════════════════════
```

## Requirements

- Python 3.8+
- `tabulate` package: `pip install tabulate`
- `anthropic` package: `pip install anthropic`
- `ANTHROPIC_API_KEY` in `.env` file

## Troubleshooting

**No props found?**
Run analysis first: `python scripts/run_analysis.py --week 12`

**API error?**
Check `.env` has: `ANTHROPIC_API_KEY=sk-ant-...`

**Can't select player twice?**
This is by design - remove existing leg first

## Full Documentation

For detailed documentation, see: `docs/CUSTOM_PARLAY_BUILDER.md`

## File Locations

- **Main Module**: `scripts/analysis/custom_parlay_builder.py`
- **CLI Entry**: `scripts/run_custom_parlay_builder.py`
- **Tracking Data**: `parlay_tracking.json`
- **Database**: `bets.db` (for calibration)

## Architecture

```
Betting Lines → PropAnalyzer (8 agents) → CustomParlayBuilder
                                                ↓
                                          User selects 6 legs
                                                ↓
                                        DependencyAnalyzer
                                                ↓
                                          ParlayTracker
                                                ↓
                                    parlay_tracking.json
```

## Tips

1. Start with 70%+ confidence props
2. Diversify across positions and games
3. Review agent breakdown for consensus
4. Pay attention to correlation adjustments
5. Track all results for calibration

## Support

See full documentation or create GitHub issue with "custom-parlay-builder" label.
