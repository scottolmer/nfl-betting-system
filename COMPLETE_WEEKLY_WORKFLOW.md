# Complete Weekly Workflow - NFL Betting System

## 🎯 Your Super Simple Workflow

### **One-Time Setup (Do Once)**
```bash
python betting_cli.py
> enable-auto-learning
> exit
```
✅ Done! Never need to do this again.

---

## 📅 Every Week

### **After Games Finish (Monday/Tuesday)**

#### 1. Upload CSV files to `data/` folder
Upload the 3 weekly stat files:
- `wk_12_passing_base.csv`
- `wk_12_rushing_base.csv`
- `wk_12_receiving_base.csv`

#### 2. Run ONE command
```bash
python betting_cli.py
> auto-learn 12
> exit
```

**That's it!** The system will:
1. Score all props from Week 12
2. Calculate agent performance
3. Adjust weights automatically
4. Save everything to database

---

### **Before Next Week's Games (Thursday/Friday)**

```bash
python betting_cli.py
> analyze-week 13 --top 100
> top-props 20
> parlays 60
```

The analysis automatically uses the **updated weights** from the auto-learning.

---

## 📊 What `auto-learn` Does

When you run `auto-learn 12`, here's what happens:

```
Step 1: Scoring Props
├─ Loads actual player stats from CSV files
├─ Compares to predicted lines
├─ Records hits/misses for each prop
└─ Stores results in database

Step 2: Calibrating Agents
├─ Calculates accuracy for each agent
├─ Detects overconfidence/underconfidence
├─ Adjusts weights based on performance
└─ Saves weight history

✅ Complete! Weights updated and ready for next week.
```

---

## 🔍 Optional: Monitor Performance

### View Current Weights
```bash
> show-weights
```

### Preview What Would Change (Dry Run)
```bash
> calibrate-agents 12
```
Shows adjustments without applying them.

### View All-Time Performance
```bash
> calibrate-agents
```
Analyzes performance across all weeks combined.

---

## 💡 Example Week-by-Week

### Week 12
```bash
# Upload: wk_12_passing_base.csv, wk_12_rushing_base.csv, wk_12_receiving_base.csv
> auto-learn 12
```
Agents learn from Week 12 performance. Weights updated.

### Week 13
```bash
# Upload: wk_13_passing_base.csv, wk_13_rushing_base.csv, wk_13_receiving_base.csv
> auto-learn 13
```
Agents learn from Week 13. Weights updated again (building on Week 12 learning).

### Week 14
```bash
# Upload: wk_14_passing_base.csv, wk_14_rushing_base.csv, wk_14_receiving_base.csv
> auto-learn 14
```
Agents continue learning. System gets better each week!

---

## 🎓 How Learning Works

### Overconfident Agent Example
```
Week 12: DVOA agent
- Predicted: 70% average confidence
- Actual hit rate: 58%
- Overconfidence: +12%
→ Weight reduced from 2.5 to 2.14

Week 13: DVOA agent (with new weight)
- Predicted: 65% average confidence
- Actual hit rate: 64%
- Overconfidence: +1%
→ Weight stays at 2.14 (well-calibrated now!)
```

### High-Accuracy Agent Example
```
Week 12: Injury agent
- Predicted: 73% average confidence
- Actual hit rate: 75%
- Overconfidence: -2% (slightly underconfident)
→ Weight increased from 1.5 to 1.51

Week 13: Injury agent (with new weight)
- Predicted: 74% average confidence
- Actual hit rate: 76%
→ Weight increased to 1.62 (continues rewarding accuracy!)
```

---

## ⚙️ Behind the Scenes

### What Gets Stored
- **All prop predictions** (before games)
- **All actual results** (after games)
- **Agent scores** for each prop (JSON format)
- **Weight adjustments** with reasons
- **Performance metrics** (accuracy, overconfidence, calibration error)

### Safety Features
- Weights bounded: 0.1 to 5.0
- Max change per week: ±0.5
- Minimum 10 samples needed for adjustment
- Gradual learning (prevents overreacting to small samples)

---

## 📋 Complete Command Reference

### Learning Commands
| Command | When to Use |
|---------|-------------|
| `auto-learn <week>` | **After games finish - ONE COMMAND!** |
| `enable-auto-learning` | One-time setup |
| `disable-auto-learning` | Turn off auto-learning |

### Analysis Commands
| Command | When to Use |
|---------|-------------|
| `analyze-week <week> --top 100` | Before games - analyze props |
| `top-props 20` | View top 20 props |
| `parlays 60` | Generate parlays (60%+ confidence) |

### Monitoring Commands
| Command | When to Use |
|---------|-------------|
| `show-weights` | See current agent weights |
| `calibrate-agents <week>` | Preview adjustments (dry run) |
| `score-props <week>` | Just score (no calibration) |

---

## ✅ Your Minimal Workflow Summary

**After each week's games:**
1. Upload 3 CSV files to `data/` folder
2. Run: `auto-learn <week>`

**Before next week's games:**
1. Run: `analyze-week <week> --top 100`
2. Run: `top-props 20`

**That's literally it!** The system handles everything else automatically.

---

## 🚀 Long-Term Benefits

### Week 1-3
System learns which agents are reliable for which situations.

### Week 4-8
Weights stabilize. Predictions become more accurate.

### Week 9-18
System is highly calibrated. Each agent has the right level of influence.

### Playoffs
Maximum accuracy! The system has learned from an entire season of data.

---

## 💬 Still Have Questions?

**Q: Do I need to run `enable-auto-learning` every week?**
No! Just once. It stays enabled.

**Q: What if I forget to run `auto-learn` one week?**
No problem! You can run it later, or run multi-week: `auto-learn 10`, then `auto-learn 11`, etc.

**Q: Can I manually adjust a weight?**
Yes! Use Python:
```python
from scripts.analysis.agent_weight_manager import AgentWeightManager
manager = AgentWeightManager("bets.db")
manager.update_weight("DVOA", 3.0, "Manual override", week=12)
```

**Q: Can I see what changed over time?**
Yes! Check weight history in the database or run:
```python
manager.get_weight_history(agent_name="DVOA", limit=20)
```

---

## 🎯 Bottom Line

**Upload CSVs → Run `auto-learn` → System gets smarter → Repeat**

Simple, automated, and continuously improving!
