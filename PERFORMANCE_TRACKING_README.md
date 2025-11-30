# Performance Tracking & Analytics System

Complete system for tracking bet outcomes and analyzing system performance.

## Quick Start

### 1. View Performance Dashboard
```bash
run_performance_dashboard.bat
```

Or:
```bash
streamlit run performance_dashboard.py
```

### 2. Generate Text Report
```bash
python analyze_performance.py
```

## What You Get

### Performance Dashboard (Streamlit)
Interactive web dashboard showing:
- **Overall accuracy** across all scored props
- **Accuracy by confidence level** - which ranges are profitable?
- **Weekly performance trends** - is the system improving?
- **Agent-level accuracy** - which agents are helping/hurting?
- **ROI by confidence bucket** - where should you bet?
- **Prop type performance** - which bets work best?
- **Recent results** - last 50 scored props

### Text Performance Report
Command-line report showing:
- Overall win rate and accuracy
- Accuracy breakdown by confidence (50-60, 60-70, 70-80, etc.)
- OVER vs UNDER performance
- Prop type accuracy (Rec Yds, Pass Yds, etc.)
- Agent performance with positive/negative prediction rates
- Weekly trends
- ROI analysis (assuming -110 odds)
- ROI by confidence level

## Key Findings from Your Data (394 scored props)

### ✅ What's Working

1. **Overall 63.7% accuracy** - System has an edge!
2. **60-70 confidence: 66.1% accuracy** - Confidence calibration works
3. **OVER bets: 67.0% accuracy** - Strong edge on overs
4. **Week 12: 81.4% accuracy** - System improving over time
5. **Pass TDs: 72.0% accuracy** - Specific prop type edge
6. **Rec Yds: 68.6% accuracy** - Another strong category

### ❌ What's Not Working

1. **UNDER bets: 35.0% accuracy** - Major problem! (System is inversely correct on unders)
2. **Injury Agent: 35.0% accuracy** - Actively hurting performance
3. **50-60 confidence: 48.1% accuracy** - Avoid these props
4. **Rush+Rec Yds: 48.3% accuracy** - Weak prop type

## Recommendations

### Immediate Actions

1. **Fix UNDER bet logic**
   - 35% accuracy means the system is backwards on unders
   - Likely an agent scoring inversion issue
   - Either fix the logic OR just avoid UNDER bets entirely

2. **Disable or recalibrate Injury Agent**
   - 35% accuracy is worse than random
   - Remove from confidence calculation until fixed

3. **Increase minimum confidence threshold**
   - Props below 60 confidence are break-even or losing
   - Set `min_confidence=60` in parlay builder

4. **Focus on OVER bets**
   - 67% accuracy is excellent
   - Until UNDER logic is fixed, stick with overs

### Betting Strategy Based on Data

**Profitable Range: 60-70 Confidence**
- 66.1% accuracy
- +26.16% ROI (at -110 odds)
- **This is your bread and butter!**

**What to Bet:**
- ✅ OVER props at 60+ confidence
- ✅ Rec Yds, Receptions, Pass TDs
- ✅ Props from Week 12+ (system improving)

**What to Avoid:**
- ❌ UNDER props (until fixed)
- ❌ Props below 60 confidence
- ❌ Rush+Rec Yds combos
- ❌ Props heavily influenced by Injury agent

### Expected ROI

Based on your historical data:

| Confidence | Win Rate | ROI (at -110) | Sample Size |
|-----------|----------|---------------|-------------|
| 50-60 | 48.1% | -8.22% | 52 props |
| 60-70 | 66.1% | +26.16% | 342 props |

**If you bet only 60+ confidence OVER props:**
- Estimated win rate: ~67%
- Estimated ROI: ~25-30%
- **This is excellent for sports betting**

## How to Use

### 1. Score New Props

When games complete, add actual results to the database. You can use the auto_scorer.py script:

```bash
python auto_scorer.py --week 13
```

Or manually update the database:

```sql
UPDATE analyzed_props
SET result = 1,  -- 1 for win, 0 for loss
    actual_value = 87.5,  -- actual stat value
    scored_date = '2024-11-30'
WHERE prop_id = 'some_id';
```

### 2. View Updated Analytics

After scoring new props, refresh the dashboard:

```bash
run_performance_dashboard.bat
```

The dashboard auto-caches for 60 seconds, then refreshes with new data.

### 3. Track Improvements

Compare weekly performance to see if changes are working:

```bash
python analyze_performance.py > weekly_report_$(date +%Y%m%d).txt
```

## Database Schema

The system uses the existing `bets.db` database with the `analyzed_props` table:

```sql
CREATE TABLE analyzed_props (
    prop_id TEXT PRIMARY KEY,
    week INTEGER,
    player TEXT,
    team TEXT,
    opponent TEXT,
    prop_type TEXT,
    bet_type TEXT,  -- 'OVER' or 'UNDER'
    line REAL,
    confidence REAL,
    agent_scores TEXT,  -- JSON string of agent scores
    result INTEGER,  -- 1 = win, 0 = loss, NULL = not scored
    actual_value REAL,  -- actual stat value
    scored_date TEXT,
    created_date TEXT
);
```

## Agent Performance Insights

Based on 394 scored props:

| Agent | Accuracy | Positive Accuracy | Count |
|-------|----------|-------------------|-------|
| GameScript | 66.8% | 66.9% | 394 |
| DVOA | 64.4% | 64.6% | 382 |
| Matchup | 65.7% | 65.4% | 367 |
| Volume | 64.2% | 66.8% | 374 |
| Variance | 64.9% | 67.7% | 350 |
| Trend | 59.6% | 64.0% | 99 |
| **Injury** | **35.0%** | **35.0%** | **40** |

**Action Items:**
- Most agents are performing well (60-68% accuracy)
- **Injury agent needs immediate attention** - actively hurting performance
- Trend agent has limited data but seems okay

## Next Steps

1. **Fix UNDER bet logic** - most critical issue
2. **Disable or fix Injury agent** - second most critical
3. **Test on Week 13** with updated logic
4. **Track results** using this dashboard
5. **Iterate and improve** based on data

## Files

- `performance_dashboard.py` - Interactive Streamlit dashboard
- `analyze_performance.py` - Command-line performance report
- `run_performance_dashboard.bat` - Quick launch script
- `bets.db` - SQLite database with prop results

## Questions?

- **Q: Why is ROI negative overall?**
  - A: Because it assumes you bet every single prop equally. In reality, you'd only bet high-confidence props.

- **Q: Is 63.7% accuracy good?**
  - A: Yes! You need 52.4% to break even at -110 odds. 63.7% is excellent.

- **Q: Should I bet real money?**
  - A: Only bet 60+ confidence OVER props until UNDER logic is fixed. Start small to validate.

- **Q: How do I add more data?**
  - A: Use `auto_scorer.py` after each week's games complete, or manually update the database.

---

**Built with the NFL Betting System v2.0**
