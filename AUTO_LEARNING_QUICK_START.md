# Automated Learning - Quick Start

## 🚀 Enable Auto-Learning (One Time Setup)

```bash
python betting_cli.py
> enable-auto-learning
```

✅ Done! The system will now automatically adjust weights after calibration.

---

## 📅 Weekly Workflow

### **After Week 10 Games Finish:**

```bash
# ONE COMMAND - scores props + calibrates agents + updates weights!
auto-learn 10

# Optional: View updated weights
show-weights
```

### **Before Week 11 Games Start:**

```bash
# Analyze Week 11 - automatically uses updated weights!
analyze-week 11 --top 100
top-props 20
```

---

## 🎯 Common Commands

| Command | What It Does |
|---------|-------------|
| `auto-learn 10` | **Score props + calibrate + update weights (ONE COMMAND!)** |
| `enable-auto-learning` | Turn on automatic weight adjustments |
| `disable-auto-learning` | Turn off automatic weight adjustments |
| `show-weights` | Display current agent weights |
| `score-props 10` | Just score props (no calibration) |
| `calibrate-agents 10` | Preview adjustments (dry run) |
| `calibrate-agents 10 --auto-apply` | Apply adjustments for Week 10 |

---

## 📊 What Gets Adjusted?

**Overconfident agents** (predict higher than actual hit rate):
- DVOA predicts 70% but only hits 58% → Weight **reduced**

**High-accuracy agents**:
- Injury agent hits 75% → Weight **increased**

**Well-calibrated agents**:
- Matchup predicts 68%, hits 68% → Weight **unchanged**

---

## 🔒 Safety Features

✅ Weights clamped between 0.1 and 5.0
✅ Max change per week: ±0.5
✅ Minimum 10 samples required
✅ Full adjustment history tracked

---

## 💡 Pro Tips

1. **Run calibration after EVERY week** - more data = better learning
2. **Check `show-weights` periodically** - see which agents are being trusted
3. **Use multi-week calibration** (`calibrate-agents --auto-apply`) for major resets
4. **Historical data is preserved** - you can always analyze trends

---

## 🧪 Test It Out

```bash
# Run the test script
python test_auto_learning.py
```

This simulates a week of performance and shows how weights adjust.

---

## ❓ Quick Troubleshooting

**Q: Are updated weights being used?**
```bash
show-weights  # Check "Last updated" timestamp
```

**Q: How do I see what changed?**
```bash
calibrate-agents 10  # Shows dry run with detailed changes
```

**Q: How do I reset to defaults?**
```python
from scripts.analysis.agent_weight_manager import AgentWeightManager
manager = AgentWeightManager("bets.db")
manager.initialize_default_weights(force=True)
```

---

## 📈 The Learning Cycle

```
Week N Games → auto-learn N → Weights Updated in DB
                                       ↓
Week N+1 Analysis → PropAnalyzer loads new weights → Better predictions!
```

---

That's it! **One command after games, then forget it.** The system learns automatically from each week's results.
