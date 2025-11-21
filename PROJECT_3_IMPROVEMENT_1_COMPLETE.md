"""
PROJECT 3 IMPROVEMENT #1: DYNAMIC CORRELATION STRENGTH MATRIX
Implementation Complete - Summary & Next Steps

Date: November 20, 2025
Status: ✅ READY FOR TESTING & INTEGRATION
"""

# ============================================================================
# WHAT WAS BUILT
# ============================================================================

This implementation replaces the flat -5% per shared driver penalty system
with a sophisticated dynamic correlation strength matrix that recognizes
that not all correlations are created equal.

PROBLEM SOLVED:
  Old: DVOA+Matchup penalty = -10% (same as Volume+Trend penalty)
  New: DVOA+Matchup = -7.5%, Volume+Trend = -3.5% (properly calibrated)

EXPECTED IMPACT:
  ✓ Better penalty calibration - strong correlations get harder penalties
  ✓ More nuanced risk assessment - catch DVOA stacks harder
  ✓ Avoid over-penalizing weak correlations
  ✓ More accurate parlay selection based on real correlation risk


# ============================================================================
# FILES CREATED / MODIFIED
# ============================================================================

1. ✅ scripts/analysis/correlation_detector.py (REWRITTEN)
   - Replaced flat penalty with dynamic strength matrix
   - Fixed penalty calculation: penalty = -5.0 * strength
   - Added safe driver extraction method (_extract_drivers)
   - Improved correlation analysis with emoji indicators
   - Better warning messages showing correlation type
   
   Key Classes:
   • CorrelationAnalyzer: Core correlation detection
   • EnhancedParlayBuilder: Integration wrapper
   • format_parlay_with_correlations(): Display formatting

2. ✅ test_correlation_strength_matrix.py (NEW)
   - Comprehensive test suite with 5 major tests
   - TEST 1: Validate all strength matrix values
   - TEST 2: Validate penalty calculations
   - TEST 3: Validate emoji/strength indicators
   - TEST 4: Full parlay correlation analysis
   - TEST 5: High-confidence parlay protection
   
   Run with: python test_correlation_strength_matrix.py

3. ✅ scripts/analysis/correlation_calibration_tracker.py (NEW)
   - Track correlation accuracy over time
   - Compare actual loss rates to expected rates
   - Recommend strength adjustments based on data
   - Export calibration data for analysis
   
   Use after each betting week to refine system

4. ✅ PROJECT_3_IMPROVEMENT_1_INTEGRATION.md (NEW)
   - Complete integration guide
   - Troubleshooting reference
   - Parameter tuning guide
   - Calibration methodology


# ============================================================================
# CORRELATION STRENGTH MATRIX
# ============================================================================

Strength Values (Multiplier for -5% base penalty):

VERY STRONG (1.3+)
  DVOA + Matchup:       1.5  ← -7.5% penalty (🔥 RED FLAG)
  DVOA + GameScript:    1.3  ← -6.5% penalty (🔥 WARNING)
  Matchup + GameScript: 1.2  ← -6.0% penalty (⚠️ CAUTION)

MODERATE (0.9-1.1)
  Injury + Volume:      1.1  ← -5.5% penalty (⚠️ MODERATE)
  DVOA + Volume:        1.0  ← -5.0% penalty (⚠️ BASELINE)
  Injury + Matchup:     0.9  ← -4.5% penalty (⚠️ MODERATE)

WEAK (0.5-0.7)
  Trend + Volume:       0.7  ← -3.5% penalty (⚡ MINOR)
  Trend + Injury:       0.6  ← -3.0% penalty (⚡ MINOR)
  Variance + Weather:   0.5  ← -2.5% penalty (⚡ MINIMAL)


# ============================================================================
# HOW IT WORKS (TECHNICAL DETAILS)
# ============================================================================

Step 1: Extract Drivers for Each Prop
  For each PropAnalysis, identify top 2 contributing agents
  Example: DVOA (35% contribution), Matchup (25% contribution)
  → Top drivers: ['DVOA', 'Matchup']

Step 2: Compare Each Parlay Leg Pair
  For each pair of legs in the parlay:
  - Find shared drivers
  - Example: Leg1 has ['DVOA', 'Matchup'], Leg2 has ['DVOA', 'Volume']
  - Shared: ['DVOA']

Step 3: Look Up Correlation Strength
  For shared driver pair, find strength multiplier
  - Single shared driver 'DVOA': use default strength 1.0
  - Pair 'DVOA'+'Matchup': lookup key = (DVOA, Matchup) → 1.5
  - Pair 'DVOA'+'Volume': lookup key = (DVOA, Volume) → 1.0

Step 4: Calculate Dynamic Penalty
  penalty = -5.0 * strength
  - DVOA+Matchup: -5.0 * 1.5 = -7.5%
  - DVOA+Volume: -5.0 * 1.0 = -5.0%
  - Trend+Volume: -5.0 * 0.7 = -3.5%

Step 5: Apply Penalty to Parlay Confidence
  Original confidence: 72%
  Correlation penalty: -7.5%
  Adjusted confidence: 64.5%
  Display: "64% (was 72%, -8% correlation penalty)"

Step 6: Generate User-Friendly Warnings
  Emoji indicators show severity:
  🔥 DVOA+Matchup: "very strong correlation"
  ⚠️ DVOA+Volume: "moderate correlation"
  ⚡ Trend+Volume: "weak correlation"


# ============================================================================
# TESTING CHECKLIST
# ============================================================================

Before using in production:

□ Step 1: Run Test Suite
  Command: python test_correlation_strength_matrix.py
  
  Expected Output:
  - TEST 1: All ✓ (strength values correct)
  - TEST 2: All ✓ (penalties match expected)
  - TEST 3: All ✓ (emoji indicators correct)
  - TEST 4: Parlay analysis works correctly
  - TEST 5: High-confidence parlays reasonable
  - Calibration guide displays

□ Step 2: Manual Testing
  Create a sample parlay with known correlations:
    Leg 1: Driver ['DVOA', 'Matchup']  (72% conf)
    Leg 2: Driver ['DVOA', 'Volume']   (70% conf)
    Leg 3: Driver ['Trend', 'Volume']  (68% conf)
  
  Expected correlations:
    • Leg1 + Leg2: DVOA shared → -5% penalty
    • Leg2 + Leg3: Volume shared → -3.5% penalty
    • Total: ~8% penalty on parlay
  
  Verify output shows:
    ✓ Original confidence: 70% (approx)
    ✓ After penalty: 62% (approx)
    ✓ Warnings show 🔥 and ⚡ indicators
    ✓ Driver attribution is correct

□ Step 3: Integration Testing
  Integrate with betting CLI and generate 10 test parlays
  Verify:
    ✓ All parlays display correlation info
    ✓ Confidence penalties are reasonable
    ✓ No errors in driver extraction
    ✓ Parlay rankings make sense

□ Step 4: Confidence Check
  Generate parlays and compare to last week's output
  Verify:
    ✓ High-correlated parlays are now properly flagged
    ✓ Penalty magnitudes seem reasonable
    ✓ Low-correlated parlays show minimal penalty
    ✓ Overall system still makes sense


# ============================================================================
# PARAMETERS TO MONITOR
# ============================================================================

As you use the system, track these values:

1. PENALTY ACCURACY
   For DVOA+Matchup correlations:
   - How often do they lose? (target: 70%+)
   - Is -7.5% penalty accurate? (adjust strength if not)

2. FALSE POSITIVES
   Are we over-penalizing certain correlation types?
   - If Volume+Trend parlays win more than expected → lower strength to 0.6
   - If they lose less → keep at 0.7

3. PARLAY QUALITY
   Overall parlay performance:
   - Are correlated parlays losing as predicted?
   - Are uncorrelated parlays winning as expected?

4. CONFIDENCE CALIBRATION
   Post-penalty confidence should be well-calibrated:
   - A 65% confidence parlay should win ~65% of the time
   - If winning more often → penalties are too harsh
   - If winning less often → penalties too lenient


# ============================================================================
# INTEGRATION INSTRUCTIONS
# ============================================================================

To use this in your betting system:

Option A: Direct Integration (Recommended for New Code)
  
  from scripts.analysis.correlation_detector import EnhancedParlayBuilder
  
  builder = EnhancedParlayBuilder()
  enhanced_parlays = builder.build_parlays_with_correlation(
      all_analyses,
      min_confidence=65,
      max_correlation_penalty=-20.0
  )


Option B: Gradual Migration (If Updating Existing Code)
  
  # Keep existing parlay builder
  optimizer = ParlayOptimizer()
  basic_parlays = optimizer.rebuild_parlays_low_correlation(...)
  
  # Add correlation analysis on top
  from scripts.analysis.correlation_detector import CorrelationAnalyzer
  analyzer = CorrelationAnalyzer()
  for parlay in basic_parlays:
      penalty, warnings = analyzer.analyze_parlay_correlations(parlay.legs)
      parlay.correlation_penalty = penalty
      parlay.correlation_warnings = warnings


# ============================================================================
# CALIBRATION WORKFLOW
# ============================================================================

Weekly Workflow:

BEFORE BETTING (Monday):
  1. Generate 10 optimized parlays with new system
  2. Note any interesting correlation patterns
  3. Verify penalties seem reasonable

AFTER BETTING (Sunday):
  1. Log each parlay result in calibration tracker
  2. Include correlation types that were detected
  3. Run: tracker.analyze_by_correlation_type()
  4. Check if any correlations need adjustment

AFTER 4-5 WEEKS:
  1. Have enough data to see patterns
  2. Review: tracker.recommend_adjustments()
  3. If recommendations appear, update CORRELATION_STRENGTH matrix
  4. Document why you adjusted each value
  5. Continue tracking to validate adjustment

AFTER SEASON:
  1. Full statistical analysis of correlation accuracy
  2. Compare actual loss rates to expected rates
  3. Generate calibration report
  4. Make final strength adjustments for next season


# ============================================================================
# COMMON ADJUSTMENTS & WHY
# ============================================================================

If you need to adjust correlation strengths after testing:

SCENARIO 1: DVOA+Matchup losses are LESS than expected
  Current: 1.5 strength (predicts 70%+ loss rate)
  Actual: 55% loss rate
  → These aren't as risky as predicted
  → Adjustment: Lower to 1.3 or 1.2
  → Reason: Maybe DVOA and Matchup are less redundant than thought

SCENARIO 2: Volume+Trend losses are MORE than expected
  Current: 0.7 strength (predicts 44% loss rate)
  Actual: 60% loss rate
  → These are riskier than predicted
  → Adjustment: Raise to 0.9 or 1.0
  → Reason: Usage and trend are more correlated than expected

SCENARIO 3: Injury+Matchup almost never loses together
  Current: 0.9 strength (predicts 48% loss rate)
  Actual: 30% loss rate
  → This correlation is weaker than expected
  → Adjustment: Lower to 0.6 or 0.5
  → Reason: Injury info might be stale or matchup already baked in

SCENARIO 4: All penalties seem too harsh
  Every parlay loses more than confidence suggests
  → Reduce base multiplier from -5.0 to -4.0
  → This uniformly reduces all penalties by 20%
  → Reason: System is being too conservative


# ============================================================================
# SUCCESS CRITERIA
# ============================================================================

Implementation is successful when:

✅ TECHNICAL
  - Test suite passes all 5 tests
  - No errors in parlay generation
  - Correlation warnings display correctly
  - Driver extraction works for all prop types

✅ PRACTICAL
  - Parlay confidence after penalty seems reasonable
  - High-correlated parlays (DVOA+Matchup) get bigger penalties
  - Low-correlated parlays (Variance+Weather) get minimal penalties
  - System is easy to use and understand

✅ CALIBRATION
  - After 3-4 weeks, can see which correlations need tuning
  - Actual parlay results match predicted loss rates
  - Can recommend specific strength adjustments
  - System improves over time with data


# ============================================================================
# NEXT STEPS
# ============================================================================

THIS WEEK:
  □ Run test suite (python test_correlation_strength_matrix.py)
  □ Review test output and verify all tests pass
  □ Integrate into betting CLI
  □ Generate test parlays and validate output

NEXT WEEK:
  □ Start tracking parlay results with calibration tracker
  □ Log each parlay's correlation_types and result
  □ Monitor for any adjustment recommendations
  □ Continue with normal betting operations

AFTER 4 WEEKS:
  □ Run correlation analysis: tracker.analyze_by_correlation_type()
  □ Review recommendations: tracker.recommend_adjustments()
  □ Make any necessary strength adjustments
  □ Document changes and rationale

AFTER SEASON:
  □ Full statistical validation of correlation strength matrix
  □ Backtesting with refined values
  □ Publish calibration report
  □ Plan improvements for next season


# ============================================================================
# QUESTIONS & TROUBLESHOOTING
# ============================================================================

Q: How do I know if penalties are calibrated correctly?
A: After 3-4 weeks of results, use calibration_tracker.analyze_by_correlation_type()
   Compare actual loss rates to expected loss rates (based on strength values).
   Differences >15% indicate adjustment is needed.

Q: Should I integrate this immediately or test more first?
A: Test first. Run test_correlation_strength_matrix.py to validate logic.
   Then integrate into betting CLI and test with sample parlays.
   After 1-2 weeks of live data, make adjustments if needed.

Q: What if a strength value is totally wrong?
A: The system self-corrects over time. Use calibration tracker to identify
   which values are inaccurate, then adjust gradually (±0.1 increments).
   Don't overthink it – the current matrix is reasonable starting point.

Q: Can I add new correlation pairs?
A: Yes! Add to CORRELATION_STRENGTH dict in correlation_detector.py.
   Default strength for new pairs: 1.0 (moderate)
   Adjust after you see actual results.

Q: What if I notice a correlation I'm not accounting for?
A: Add it to the matrix with initial strength 1.0, then monitor.
   After sufficient data, calibration tracker will tell you if 1.0 is right.


Made with 🔧 by Scott's NFL Betting System
Project 3 Improvement 1: Dynamic Correlation Strength Matrix
November 2025 | Ready for Testing & Integration
"""
