# 🏈 NFL Betting Analysis System

**Automated prop betting analysis using DVOA, projections, and live odds**

## 🚀 Quick Start

### One-Command Full Analysis
```bash
# Fetch live odds + analyze + generate betting card
python scripts\run_analysis.py --week 7

# Use existing odds data (skip API fetch)
python scripts\run_analysis.py --week 7 --skip-fetch
```

## 📋 Manual Workflow

### Step 1: Fetch Live Odds (Optional)
```bash
python scripts\fetch_odds.py --week 7
```

### Step 2: Generate Betting Card
```bash
python scripts\generate_betting_card.py
```

## 🎯 What You Get

### Automated Analysis
- ✅ 1,000+ props analyzed in seconds
- ✅ 8 intelligent agents (DVOA, Matchup, Volume, Variance, etc.)
- ✅ Confidence scoring (50-100 scale)
- ✅ Position-specific analysis (WR1/WR2/WR3, TE, RB, QB)

### Actionable Recommendations
- **2 two-leg parlays** (correlated + uncorrelated)
- **2 three-leg parlays** (aggressive + balanced)
- **2 four-leg parlays** (conservative + high-risk)
- **Risk labels** (LOW/MODERATE/HIGH)
- **Unit sizing** (0.5-2.0 units per bet)

### Output Files
- `data/week{X}_betting_card.txt` - Complete betting card
- `data/betting_lines_wk_{X}_live.csv` - Raw odds data

## 📊 System Architecture

### Multi-Agent Analysis
1. **DVOA Agent** (×2.0 weight) - Team offensive/defensive strength
2. **Matchup Agent** (×1.8 weight) - Position-specific matchups
3. **Volume Agent** (×1.2 weight) - Target share & snap counts
4. **GameScript Agent** (×1.3 weight) - Game total & spread analysis
5. **Variance Agent** (×0.8 weight) - Prop type reliability
6. **Trend Agent** (×1.0 weight) - Recent performance
7. **Injury Agent** (×1.5 weight) - Health status impact
8. **Weather Agent** (×0.5 weight) - Outdoor game conditions

### Confidence Calculation
```
Final Confidence = Weighted Average of Active Agents
```
- Only agents with meaningful opinions (non-neutral) are weighted
- Prevents neutral agents from diluting strong signals

## 🔧 Configuration

### Data Requirements
Place these files in `/data`:
- `DVOA_Off_wk_{X}.csv` - Offensive DVOA rankings
- `DVOA_Def_wk_{X}.csv` - Defensive DVOA rankings
- `Def_vs_WR_wk_{X}.csv` - WR-specific defensive rankings
- `NFL_Projections_Wk_{X}_updated.csv` - Player projections
- `week{X}_injury_report.txt` - Injury statuses

### API Configuration
The system uses the DraftKings public API (no authentication required).

Rate limiting: 1 request/second (automatic)

## 📈 Example Output

```
🎯 ACTIONABLE PARLAY RECOMMENDATIONS

2-LEG PARLAYS
--------------
PARLAY 21 - MODERATE RISK
Combined Confidence: 80
Recommended Bet: 1.5 units ($15)

  Leg 1: Justin Jefferson (LAC) - Rec Yds OVER 79.5
  Leg 2: Jordan Addison (LAC) - Rec Yds OVER 55.5

  Rationale:
    • Same-game stack: LAC vs MIN
    • Elite passing offense (+23.7% DVOA)
    • MIN allows +172.9% DVOA vs WR1
```

## 🧪 Testing

### Test API Connection
```bash
python scripts\api\draftkings_api.py
```

### Test Individual Player
```bash
python scripts\debug_player.py
```

### Check Game Variety
```bash
python scripts\check_variety.py
```

## 🔍 Diagnostic Tools

### Find Elite Props
```bash
python scripts\find_elite_props.py
```
Shows:
- Top 10 highest confidence props
- Elite volume players (28%+ targets)
- Premium matchups (DVOA 30+)

### Clear Cache
```bash
python scripts\clear_all_cache.py
```

## 💡 Betting Strategy

### Recommended Approach
1. **Start with 2-leg parlays** (higher hit rate)
2. **Use LOW/MODERATE risk plays** (2-3 units total)
3. **Diversify across games** (uncorrelated better for bankroll)
4. **Track results** (adjust confidence thresholds over time)

### Risk Management
- Never bet more than 5-10% of bankroll per day
- Start small (0.5-1.0 unit bets) until system is validated
- Track all bets for performance analysis

## 📝 Weekly Workflow

### Thursday
```bash
# Update week7 → week8 in filenames
python scripts\run_analysis.py --week 8
```

### Sunday Morning
```bash
# Refresh odds for latest lines
python scripts\run_analysis.py --week 8
```

## 🛠️ Troubleshooting

### "No props found"
- Check internet connection
- Verify DraftKings API is accessible
- Use `--skip-fetch` to use existing data

### "File not found"
- Ensure all CSV files are in `/data` directory
- Check week number matches filename

### "Low confidence props"
- Normal for some weeks (defensive matchups)
- Lower `min_confidence` in `generate_betting_card.py` (line 36)

## 📦 Dependencies

```bash
pip install pandas numpy requests
```

## 🎓 Understanding the System

### What Makes a High-Confidence Prop?
1. **Elite matchup** (defense allows 30+ DVOA vs position)
2. **High volume** (25%+ target share or 75%+ snaps)
3. **Strong offense** (team +15% DVOA)
4. **Favorable game script** (high total, appropriate spread)

### Why Same-Game Parlays?
- **Correlation bonus** (+3-5 confidence)
- **Higher variance** (all-or-nothing)
- **Best for:** Shootout games, dominant offenses

### Why Uncorrelated Parlays?
- **Lower variance** (independent events)
- **Better bankroll management**
- **Best for:** Conservative approach, diversification

## 🏆 Success Metrics

The system aims for:
- **60-65% hit rate** on 70+ confidence props
- **4-6% ROI** across all bets
- **75+ confidence** = "Strong" plays

## ⚠️ Disclaimer

This system is for **informational purposes only**. Sports betting involves risk. Never bet more than you can afford to lose. Past performance does not guarantee future results.

## 🤝 Contributing

Found a bug? Have a suggestion?
- Open an issue
- Submit a pull request
- Share your results

## 📄 License

MIT License - Use freely, modify as needed

---

**Good luck! 🍀**

*Built with ❤️ for smart sports bettors*
