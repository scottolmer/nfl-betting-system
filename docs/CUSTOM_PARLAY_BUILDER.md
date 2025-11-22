# Custom Parlay Builder

## Overview

The Custom Parlay Builder is an interactive CLI tool that allows you to manually create 6-leg parlays from the pool of all analyzed props for a given week. This feature is designed for situations where DraftKings lines don't match your system-generated parlays, requiring you to substitute different props while still benefiting from correlation analysis and confidence scoring.

## Features

### 1. **View All Analyzed Props**
- Display all props analyzed by the 8-agent system for any week
- Multiple sorting options: confidence (default), position, player, game
- Filter by: position, stat type, player name, minimum confidence
- Shows confidence scores, top contributing agents, and matchup details

### 2. **Interactive Leg Selection**
- User-friendly CLI for selecting exactly 6 legs
- Multiple search methods:
  - Browse all props (paginated display)
  - Search by player name (partial matching)
  - Filter by position (QB, RB, WR, TE, K)
  - Filter by stat type (Pass Yds, Rush Yds, etc.)
- Real-time validation: prevents duplicate players
- Running count: "X of 6 legs selected"
- Ability to remove/replace legs before finalizing

### 3. **Correlation Analysis**
- Automatically runs Claude Sonnet correlation analysis on your custom parlay
- Calculates correlation-adjusted confidence score
- Provides detailed explanations of correlation concerns
- Shows individual agent breakdowns per leg
- Displays raw vs adjusted confidence scores

### 4. **Save & Track Custom Parlays**
- Saves to `parlay_tracking.json` with "custom" type flag
- Includes in weekly exports for calibration analysis
- Tracks agent breakdown data for system learning
- Compatible with existing parlay tracking infrastructure

### 5. **Edge Case Handling**
- Blocks selecting same player twice (per existing rules)
- Validates 6 legs before allowing analysis
- Graceful handling of cancelled operations
- Clear error messages and user feedback

## Installation

The Custom Parlay Builder is included in the main NFL betting system. Ensure you have the required dependencies:

```bash
pip install tabulate anthropic
```

Make sure your `ANTHROPIC_API_KEY` is set in your `.env` file for correlation analysis:

```bash
ANTHROPIC_API_KEY=your_key_here
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Build a custom parlay for week 12
python scripts/run_custom_parlay_builder.py --week 12

# Specify year
python scripts/run_custom_parlay_builder.py --week 12 --year 2024

# Preview available props without building
python scripts/run_custom_parlay_builder.py --week 12 --preview

# Set minimum confidence threshold
python scripts/run_custom_parlay_builder.py --week 12 --min-confidence 60
```

#### Command Line Options
- `--week`: NFL week number (required)
- `--year`: Year (default: 2024)
- `--preview`: Preview available props without building a parlay
- `--min-confidence`: Minimum confidence threshold (default: 50)

### Python API

You can also use the Custom Parlay Builder programmatically:

```python
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.custom_parlay_builder import run_custom_parlay_builder

# Load and analyze props
loader = NFLDataLoader()
context = loader.load_all_data(week=12)

analyzer = PropAnalyzer()
analyzed_props = analyzer.analyze_all_props(context, min_confidence=50)

# Run interactive builder
parlay_id = run_custom_parlay_builder(analyzed_props, week=12, year=2024)
```

### Advanced Usage with CustomParlayBuilder Class

```python
from scripts.analysis.custom_parlay_builder import CustomParlayBuilder

# Initialize builder
builder = CustomParlayBuilder(analyzed_props, week=12, year=2024)

# Display props with custom filtering
builder.display_all_props(
    sort_by="confidence",
    filter_position="QB",
    min_confidence=60,
    limit=20
)

# Manually add legs
for i in range(6):
    builder.select_leg_interactive()

# Analyze the custom parlay
analysis_results = builder.analyze_custom_parlay()

# Save the parlay
parlay_id = builder.save_custom_parlay(
    analysis_results,
    payout_odds=4000  # +4000 for 6-leg parlay
)
```

## User Workflow Example

### Step 1: View Available Props
```
📊 ANALYZED PROPS - Week 12 (156 props)
═══════════════════════════════════════════════════════════
#   Player          Pos  Stat Type    Line   Dir  Conf    Game
───────────────────────────────────────────────────────────
1   Mahomes         QB   Pass Yds     285.5  OVER 82%    KC vs LV
2   McCaffrey       RB   Rush Yds     95.5   OVER 78%    SF vs SEA
3   Jefferson       WR   Rec Yds      88.5   OVER 76%    MIN vs DET
...
```

### Step 2: Select Legs Interactively
```
🏈 SELECT LEG (0/6 selected)
═══════════════════════════════════════════════════════

How would you like to find a prop?
  1. Browse all props
  2. Search by player name
  3. Filter by position
  4. Filter by stat type
  5. Cancel / Go back

Enter choice (1-5): 2
Enter player name (partial match): mahomes

✓ Found 4 props matching 'mahomes'
...
✅ Added: Mahomes Pass Yds OVER 285.5
```

### Step 3: Analyze Correlation
```
🔍 ANALYZING CUSTOM PARLAY...
═══════════════════════════════════════════════════════

📊 Raw Confidence (average): 75.3%

🤖 Running correlation analysis with Claude...

📈 CORRELATION ANALYSIS RESULTS
═══════════════════════════════════════════════════════
Raw Confidence:        75.3%
Correlation Adjust:    -2.0
Adjusted Confidence:   73.3%
Recommendation:        ACCEPT

Reasoning: Minor correlation detected between KC QB and WR in same game.
          Slight downward adjustment applied.
═══════════════════════════════════════════════════════
```

### Step 4: Save Parlay
```
💾 Save this custom parlay? (y/n): y
Enter payout odds (default +4000 for 6-leg): 4000

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

## Data Integration

### Parlay Tracking (JSON)

Custom parlays are saved to `parlay_tracking.json` with the following structure:

```json
{
  "parlay_id": "CUST_W12_a7f3e2d1_v1",
  "week": 12,
  "year": 2024,
  "parlay_type": "custom",
  "props": [...],
  "raw_confidence": 75.3,
  "effective_confidence": 73.3,
  "correlations": [
    {
      "type": "custom_parlay_analysis",
      "adjustment": -2.0,
      "reasoning": "Minor correlation detected..."
    }
  ],
  "payout_odds": 4000,
  "kelly_bet_size": 2.33,
  "agent_breakdown": {
    "DVOA": {"raw_score": 78, "weight": 0.20},
    "Matchup": {"raw_score": 72, "weight": 0.15},
    ...
  },
  "bet_on": false,
  "result": null
}
```

### Performance Tracking (SQLite)

Custom parlays are also compatible with the SQLite performance tracker (`bets.db`) for calibration analysis. The `parlay_type` field will be set to "custom" to distinguish from system-generated parlays.

## Tracking & Results

### Mark as Bet

After placing the bet on DraftKings:

```python
from scripts.analysis.parlay_tracker import ParlayTracker

tracker = ParlayTracker()
tracker.mark_bet("CUST_W12_a7f3e2d1_v1", bet_amount=10.0)
```

### Log Results

After games complete:

```python
tracker.mark_result(
    parlay_id="CUST_W12_a7f3e2d1_v1",
    result="won",  # or "lost"
    prop_results=[
        {"player": "Mahomes", "stat_type": "Pass Yds", "hit": True},
        {"player": "McCaffrey", "stat_type": "Rush Yds", "hit": True},
        ...
    ],
    actual_payout=410.0
)
```

### View Statistics

```python
# Get statistics for custom parlays only
stats = tracker.get_statistics(parlay_type="custom", bet_only=True)

# Compare custom vs system-generated parlays
custom_stats = tracker.get_statistics(parlay_type="custom")
system_stats = tracker.get_statistics(parlay_type="traditional")
```

## Calibration & Learning

Custom parlays are included in the weekly calibration export, allowing you to:

1. **Compare Performance**: Custom vs system-generated parlays
2. **Agent Analysis**: Which agents perform best in manual selections
3. **Correlation Accuracy**: How well correlation adjustments predict outcomes
4. **Confidence Calibration**: Are custom parlays over/under-confident?

### Export for Analysis

```python
tracker.export_to_csv("custom_parlays_export.csv")
```

## Tips & Best Practices

### 1. **Use High-Confidence Props**
- Start with props that have 70%+ confidence from the system
- The correlation analysis will adjust for dependencies

### 2. **Diversify Positions**
- Mix QB, RB, WR, TE props for lower correlation
- Avoid stacking multiple players from the same team/game

### 3. **Check Agent Breakdown**
- Look for props where multiple agents agree (consensus)
- Be cautious if only one agent is driving high confidence

### 4. **Review Correlation Analysis**
- Pay attention to the adjusted confidence score
- "AVOID" recommendations indicate high correlation risk

### 5. **Track Everything**
- Always mark bets and log results for calibration
- Review performance monthly to refine your selection strategy

## Troubleshooting

### No Props Available
```
❌ No props found after loading! Check your data files.
```
**Solution**: Ensure betting lines CSV exists for the specified week:
- File format: `data/betting_lines_wk_12_*.csv`
- Run `scripts/run_analysis.py --week 12` first to fetch/analyze props

### API Key Error
```
❌ Correlation analysis failed: Invalid API key
```
**Solution**: Set your Anthropic API key in `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### Duplicate Player Error
```
❌ Cannot add: Player already selected
```
**Solution**: This is by design. Remove the existing leg first if you want to select a different prop for the same player.

### Insufficient Legs
```
❌ Need exactly 6 legs selected (currently have 4)
```
**Solution**: Continue adding legs until you reach 6 before analyzing.

## Architecture

### Key Components

1. **CustomParlayBuilder** (`custom_parlay_builder.py`)
   - Main builder class with interactive CLI
   - Display, selection, analysis, and save functions

2. **ParlayTracker** (`parlay_tracker.py`)
   - JSON-based parlay persistence
   - Supports "custom" parlay type

3. **DependencyAnalyzer** (`dependency_analyzer.py`)
   - Claude-powered correlation detection
   - Adjusts confidence based on dependencies

4. **PropAnalyzer** (`orchestrator.py`)
   - 8-agent analysis system
   - Provides analyzed props to builder

### Data Flow

```
Betting Lines CSV
    ↓
NFLDataLoader
    ↓
PropAnalyzer (8 agents)
    ↓
List[PropAnalysis]
    ↓
CustomParlayBuilder
    ↓
User Selection (6 legs)
    ↓
DependencyAnalyzer (correlation)
    ↓
ParlayTracker (save as "custom")
    ↓
parlay_tracking.json + bets.db
```

## Future Enhancements

Potential improvements for future versions:

- [ ] Support for 2-5 leg custom parlays (currently 6-leg only)
- [ ] Save/load draft parlays for later editing
- [ ] Batch import from DraftKings bet slip
- [ ] Visual correlation heatmap
- [ ] Historical performance by user vs system selections
- [ ] ML-based prop recommendations based on user preferences

## Support

For issues or questions:
- Check existing GitHub issues
- Create new issue with "custom-parlay-builder" label
- Include week number, error message, and steps to reproduce

## License

This feature is part of the NFL Betting System V2 and follows the same license as the main project.
