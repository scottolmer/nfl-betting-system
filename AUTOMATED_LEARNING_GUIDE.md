# Automated Learning System - Complete Guide

## Overview

Your NFL betting system now features **fully automated learning** that adjusts agent weights based on historical performance. The system learns from each week's results and automatically improves predictions over time.

---

## How It Works

### 1. **Score Props After Each Week**
After games conclude, score the props to record actual results:
```bash
score-props 10
```

This compares predictions to actual player stats from CSV files and records:
- Whether each prop hit (1) or missed (0)
- The actual stat value vs. the predicted line
- All 8 agent scores for each prop

### 2. **Calibrate Agents**
Analyze agent performance and apply weight adjustments:
```bash
calibrate-agents 10 --auto-apply
```

The system will:
- Calculate accuracy for each agent
- Detect overconfidence/underconfidence
- Automatically adjust weights
- Store adjustment history

### 3. **Next Week's Analysis Uses Updated Weights**
When you analyze Week 11 props, the system automatically loads the updated weights from the database.

---

## CLI Commands

### **View Current Weights**
```bash
show-weights
```

Displays:
```
============================================================
CURRENT AGENT WEIGHTS
============================================================
DVOA             2.14  █████████████████████
Matchup          2.10  █████████████████████
Volume           1.56  ███████████████
Injury           1.51  ███████████████
GameScript       1.15  ███████████
Trend            0.71  ███████
Variance         0.65  ██████
Weather          0.44  ████
============================================================
Auto-learning: ENABLED
============================================================
```

### **Calibrate Agents (Manual Mode)**
```bash
calibrate-agents 10
```
Shows what adjustments would be made (dry run - no changes applied).

### **Calibrate Agents (Auto-Apply)**
```bash
calibrate-agents 10 --auto-apply
```
Calculates and applies weight adjustments immediately.

### **Enable Global Auto-Learning**
```bash
enable-auto-learning
```
After this, `calibrate-agents` will ALWAYS apply adjustments automatically.

### **Disable Global Auto-Learning**
```bash
disable-auto-learning
```
Revert to manual mode (dry run by default).

### **Multi-Week Calibration**
```bash
calibrate-agents --auto-apply
```
Analyzes ALL weeks combined (no week number = all-time performance).

---

## Adjustment Logic

### **Weight Adjustment Formula**

```python
adjustment = -overconfidence * 3.0

# Bonus for high accuracy (>70%)
if accuracy > 0.70:
    adjustment += (accuracy - 0.70) * 2.0

# Penalty for low accuracy (<50%)
if accuracy < 0.50:
    adjustment -= (0.50 - accuracy) * 2.0

new_weight = current_weight + adjustment
```

### **Examples**

#### **Overconfident Agent**
- Agent predicts 70% confidence on average
- Actual hit rate: 58%
- Overconfidence: +12%
- **Result:** Weight reduced by ~0.36

#### **High-Accuracy Agent**
- Accuracy: 75%
- Overconfidence: -2% (slightly underconfident)
- **Result:** Weight increased by ~0.10 (accuracy bonus)

#### **Well-Calibrated Agent**
- Accuracy: 68%
- Overconfidence: +1% (negligible)
- **Result:** No change

---

## Safety Constraints

### **Built-in Protections**

1. **Weight Bounds:** 0.1 ≤ weight ≤ 5.0
2. **Max Adjustment Per Week:** ±0.5 (prevents extreme swings)
3. **Minimum Sample Size:** 10 legs required for adjustment
4. **Gradual Learning:** Uses 3.0x multiplier (reduced from 5.0 for smoother learning)

### **Insufficient Data Handling**

If an agent has <10 samples in a week:
```
⏭️ DVOA            2.50 → 2.50 (no change)
   Reason: Insufficient data (8 < 10)
```

---

## Database Schema

### **New Tables**

#### **agent_weights**
Stores current active weights:
```sql
CREATE TABLE agent_weights (
    agent_name TEXT PRIMARY KEY,
    weight REAL NOT NULL,
    last_updated TEXT NOT NULL,
    total_legs_analyzed INTEGER DEFAULT 0,
    cumulative_accuracy REAL DEFAULT 0.0,
    notes TEXT
)
```

#### **agent_weight_history**
Audit trail of all adjustments:
```sql
CREATE TABLE agent_weight_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_name TEXT NOT NULL,
    old_weight REAL NOT NULL,
    new_weight REAL NOT NULL,
    adjustment_reason TEXT,
    week INTEGER,
    accuracy REAL,
    overconfidence REAL,
    sample_size INTEGER,
    timestamp TEXT NOT NULL
)
```

#### **learning_config**
System configuration:
```sql
CREATE TABLE learning_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
```

---

## Integration with Existing System

### **Modified Files**

1. **`agent_weight_manager.py`** (NEW)
   - AgentWeightManager class
   - Auto-adjustment logic
   - Weight history tracking

2. **`agent_calibrator.py`** (UPDATED)
   - Now calls AgentWeightManager
   - Supports `--auto-apply` flag
   - Shows adjustment summaries

3. **`orchestrator.py`** (UPDATED)
   - PropAnalyzer now loads weights from database
   - `use_dynamic_weights=True` by default
   - Logs loaded weights on startup

4. **`betting_cli.py`** (UPDATED)
   - New commands: `enable-auto-learning`, `disable-auto-learning`, `show-weights`
   - Updated `calibrate-agents` to support `--auto-apply`

---

## Weekly Workflow

### **Complete Automated Learning Cycle**

```bash
# Monday: Games are done, Week 10 stats are available

# Step 1: Score all props from Week 10
score-props 10

# Step 2: Calibrate and auto-adjust weights
calibrate-agents 10 --auto-apply

# Step 3: View updated weights
show-weights

# Thursday: Analyze Week 11 props (uses updated weights automatically)
analyze-week 11 --top 100
```

---

## Monitoring & Debugging

### **View Weight History**
```python
from scripts.analysis.agent_weight_manager import AgentWeightManager

manager = AgentWeightManager("bets.db")
history = manager.get_weight_history(agent_name="DVOA", limit=20)

for entry in history:
    print(f"{entry['week']}: {entry['old_weight']:.2f} → {entry['new_weight']:.2f}")
    print(f"  Reason: {entry['reason']}")
```

### **Check Current State**
```python
manager = AgentWeightManager("bets.db")
weights = manager.get_current_weights()
print(weights)
# {'DVOA': 2.14, 'Matchup': 2.10, ...}

auto_enabled = manager.is_auto_learning_enabled()
print(f"Auto-learning: {auto_enabled}")
```

---

## Example Output

### **Calibration with Auto-Apply**

```
============================================================
CURRENT AGENT WEIGHTS
============================================================
DVOA             2.50  █████████████████████████
Matchup          2.00  ████████████████████
...

================================================================================
🔬 AGENT RECALIBRATION ANALYSIS
================================================================================
Week 10 | 45 legs analyzed
--------------------------------------------------------------------------------

AGENT PERFORMANCE RANKING:
1. Trend           🔴 (overconfident)
   Accuracy:          48.0% (12/25 hits)
   Calibration Error: 0.180
   Overconfidence:   +0.150
   → REDUCE weight (agent too bullish)

2. DVOA            🔴 (overconfident)
   Accuracy:          65.0% (16/25 hits)
   Calibration Error: 0.145
   Overconfidence:   +0.120
   → REDUCE weight (agent too bullish)

3. Injury          ✅ (well-calibrated)
   Accuracy:          75.0% (15/20 hits)
   Calibration Error: 0.042
   Overconfidence:   +0.030
   → OK (no adjustment needed)

================================================================================
AUTOMATED WEIGHT ADJUSTMENTS
================================================================================

⬇️ Trend           1.20 → 0.71 (-0.49)
   Reason: Overconfident (+15.0%) - reducing weight
   Stats: 48.0% accuracy, +15.0% overconfidence, 22 samples

⬇️ DVOA            2.50 → 2.14 (-0.36)
   Reason: Overconfident (+12.0%) - reducing weight
   Stats: 65.0% accuracy, +12.0% overconfidence, 25 samples

✅ Injury          1.50 → 1.51 (no change)
   Reason: Well-calibrated (no adjustment needed)
   Stats: 75.0% accuracy, +3.0% overconfidence, 20 samples

================================================================================

✅ UPDATED WEIGHTS:
DVOA             2.14  █████████████████████
Trend            0.71  ███████
...
```

---

## Advanced Usage

### **Programmatic Access**

```python
from scripts.analysis.agent_weight_manager import AgentWeightManager

manager = AgentWeightManager("bets.db")

# Manual weight update
manager.update_weight(
    agent_name="DVOA",
    new_weight=2.5,
    reason="Manual override - reset to baseline",
    week=10
)

# Simulate adjustments
agent_performance = {
    'DVOA': {
        'accuracy': 0.68,
        'overconfidence': 0.05,
        'sample_size': 30
    }
}

adjustments = manager.auto_adjust_weights(
    agent_performance=agent_performance,
    week=11,
    dry_run=True  # Preview only
)

# Apply adjustments
manager.auto_adjust_weights(
    agent_performance=agent_performance,
    week=11,
    dry_run=False
)
```

---

## Performance Tracking

The system tracks:
- **Agent-level:** Accuracy, calibration error, overconfidence
- **Prop-level:** Hit rate by confidence bucket, prop type, bet type (OVER/UNDER)
- **Historical:** Weight evolution over time
- **Correlation:** Parlay loss rates vs. predicted correlation strength

All metrics are stored in `bets.db` for long-term analysis.

---

## Troubleshooting

### **Weights not loading in orchestrator**
```python
# Check if dynamic weights are enabled
analyzer = PropAnalyzer(db_path="bets.db", use_dynamic_weights=True)
```

### **Auto-learning not applying**
```bash
# Check config
show-weights
# Should show: Auto-learning: ENABLED

# If disabled, enable it
enable-auto-learning
```

### **Reset to defaults**
```python
manager = AgentWeightManager("bets.db")
manager.initialize_default_weights(force=True)
```

---

## Future Enhancements

Possible additions:
1. **Confidence Rescaling:** Auto-rescale all confidences if system is consistently over/underconfident
2. **Prop-Type Specific Weights:** Different weights for Pass Yds vs. Rush Yds
3. **Correlation Strength Auto-Adjustment:** Update correlation matrix based on actual parlay results
4. **Meta-Learning:** Adjust adjustment formula parameters based on long-term performance

---

## Key Takeaways

✅ **Automated:** Weights adjust automatically after each week
✅ **Safe:** Built-in constraints prevent extreme changes
✅ **Transparent:** Full history of all adjustments
✅ **Flexible:** Can be enabled/disabled or run manually
✅ **Integrated:** Works seamlessly with existing workflow

The system **learns from every bet** and **improves over time** without manual intervention!
