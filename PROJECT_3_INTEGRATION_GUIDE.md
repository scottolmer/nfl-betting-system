# PROJECT 3 INTEGRATION GUIDE

Quick steps to enable correlation detection in your system.

## Step 1: Verify Updated Files ✅

These files have been updated:
- `scripts/analysis/models.py` - Added `top_contributing_agents` field
- `scripts/analysis/orchestrator.py` - Added `_calculate_top_contributing_agents()` method
- `scripts/analysis/correlation_detector.py` - NEW FILE with correlation detection logic

## Step 2: Update Your Parlay Builder Call

In whatever file builds parlays (`betting_cli.py`, `run_analysis.py`, or similar):

### Old Code:
```python
from scripts.analysis.parlay_builder import ParlayBuilder

analyses = analyzer.analyze_all_props(context)
builder = ParlayBuilder()
parlays = builder.build_parlays(analyses, min_confidence=58)
output = builder.format_parlays_for_betting(parlays)
```

### New Code (with Correlation Detection):
```python
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.analysis.correlation_detector import EnhancedParlayBuilder

analyses = analyzer.analyze_all_props(context)

# Use enhanced builder with correlation detection
enhanced_builder = EnhancedParlayBuilder()
parlays = enhanced_builder.build_parlays_with_correlation(
    analyses,
    min_confidence=58,
    max_correlation_penalty=-10.0
)

# Use standard formatter (mostly compatible)
builder = ParlayBuilder()
output = builder.format_parlays_for_betting(parlays)

# The output will now include correlation adjustments automatically
```

### Optional: Enhanced Display with Correlation Warnings
```python
from scripts.analysis.correlation_detector import format_parlay_with_correlations

# For custom output with full correlation details:
for leg_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
    for parlay in parlays[leg_type]:
        lines = format_parlay_with_correlations(parlay)
        for line in lines:
            print(line)
```

## Step 3: Test It

Run the test to verify everything works:
```bash
python test_project_3.py
```

You should see:
- ✅ Detects correlated props
- ✅ No false positives on independent props
- ✅ Correct penalty calculations
- ✅ Proper warning messages

## Step 4: Monitor Results

After enabling correlation detection:

1. **Compare outputs** - Your parlays will now show -5% to -10% lower confidence
2. **Track hit rates** - These more honest confidence scores should match actual performance better
3. **Calibrate if needed** - If penalties seem off, adjust the `-5` multiplier in `CorrelationAnalyzer.calculate_correlation_risk()`

## Configuration Options

### Adjust Correlation Penalty
In `build_parlays_with_correlation()`:
```python
# Cap penalty at -15% instead of -10%
parlays = enhanced_builder.build_parlays_with_correlation(
    analyses,
    max_correlation_penalty=-15.0  # More aggressive penalty
)
```

### Customize Driver Matching
In `CorrelationAnalyzer.calculate_correlation_risk()`:
```python
# Change from top 2 drivers to top 3
leg1_drivers = {agent[0] for agent in leg1.top_contributing_agents[:3]}
leg2_drivers = {agent[0] for agent in leg2.top_contributing_agents[:3]}
```

### Change Penalty Per Driver
In `CorrelationAnalyzer.calculate_correlation_risk()`:
```python
# Change from -5 to -7.5 per shared driver
correlation_penalty = -7.5 * len(shared_drivers)
```

## Backward Compatibility

✅ **Safe to enable** - The enhanced builder still generates the same parlay legs as the standard builder. It only:
1. Calculates top_contributing_agents (new metadata)
2. Analyzes correlations (new analysis)
3. Adjusts confidence (better accuracy)
4. Adds warnings (better transparency)

You can toggle back to standard builder anytime without issues.

## Verification Checklist

After integration:

- [ ] System imports new `correlation_detector.py` without errors
- [ ] `test_project_3.py` runs and passes all tests
- [ ] Parlays display correlation adjustments in output
- [ ] Confidence numbers are lower (typical -5 to -10% reduction)
- [ ] Correlation warnings appear for same-game parlays
- [ ] System still generates 10 parlays as expected
- [ ] No performance degradation (correlation analysis <100ms)

## Questions & Troubleshooting

**Q: Will this break my existing system?**
A: No. It's a drop-in replacement that only adds correlation detection.

**Q: Why are my parlays showing lower confidence?**
A: Because they're more honest! The standard builder ignored correlations, which is why your actual hit rate was lower than reported confidence.

**Q: Can I disable correlation detection for specific parlays?**
A: Yes - modify `analyze_parlay_correlations()` to skip analysis for certain parlay types.

**Q: Should I use this with Project 1 (neutral score fix)?**
A: Yes! Do Project 1 first to clean up signals, then Project 3 will be more accurate.

---

**Ready to enable?** Just update your parlay builder call and you're done! 🎯
