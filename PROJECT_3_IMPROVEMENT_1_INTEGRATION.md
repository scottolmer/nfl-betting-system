"""
PROJECT 3 IMPROVEMENT #1: DYNAMIC CORRELATION STRENGTH MATRIX
Integration & Implementation Guide

This document explains how the new dynamic correlation system works and how to
integrate it with your existing parlay generation pipeline.

Generated: November 2025
Status: Ready for Integration
"""

# ============================================================================
# WHAT WAS IMPROVED
# ============================================================================

OLD SYSTEM (Flat Penalty):
  - DVOA + Matchup = -5% * 2 drivers = -10%
  - Volume + Trend = -5% * 2 drivers = -10%  ← Same penalty despite different risk!
  - Result: Over-penalizes weak correlations, under-penalizes strong ones

NEW SYSTEM (Dynamic Penalty):
  - DVOA + Matchup = -5% * 1.5 (strength) = -7.5% per pair
  - Volume + Trend = -5% * 0.7 (strength) = -3.5% per pair  ← Different!
  - Result: Accurate risk assessment based on correlation type


# ============================================================================
# CORE CHANGES
# ============================================================================

FILE: scripts/analysis/correlation_detector.py

1. CORRELATION_STRENGTH MATRIX (lines ~30-50)
   - Maps agent pairs to correlation strength (0.5 to 1.5)
   - Higher strength = stronger correlation = bigger penalty
   - Examples:
     ('DVOA', 'Matchup'): 1.5   # Very strong (same fundamental weakness)
     ('Trend', 'Volume'): 0.7   # Weak (different signal types)

2. PENALTY FORMULA (line ~61-65)
   penalty = -5.0 * strength
   
   For a pair of shared drivers:
   - DVOA + Matchup (strength 1.5) → -7.5%
   - DVOA + Volume (strength 1.0) → -5.0%
   - Volume + Trend (strength 0.7) → -3.5%

3. _extract_drivers() METHOD (line ~120-135)
   Safely extracts top 2 contributing agents from any prop analysis
   Handles both new format (top_contributing_agents) and fallback

4. analyze_parlay_correlations() (line ~193-245)
   For each leg pair in parlay:
   - Find shared drivers
   - Look up correlation strength for that driver pair
   - Apply dynamic penalty
   - Generate emoji-coded warnings (🔥 ⚠️ ⚡)


# ============================================================================
# INTEGRATION CHECKLIST
# ============================================================================

✓ Step 1: Files Already Updated
  - correlation_detector.py: UPDATED ✓
  - test_correlation_strength_matrix.py: CREATED ✓

□ Step 2: Test the System
  Run: python test_correlation_strength_matrix.py
  
  Verify:
  - Test 1: All strength values are correct (should see ✓ for all)
  - Test 2: Penalties calculate correctly (DVOA+Matchup = -7.5%, etc)
  - Test 3: Emoji indicators match strength levels
  - Test 4: 3-leg parlay analysis detects all correlations correctly
  - Test 5: High-confidence parlays get reasonable penalties

□ Step 3: Integration into Betting CLI
  In your betting_cli_with_live_odds.py (or equivalent):
  
  BEFORE: Using ParlayOptimizer directly
    optimizer = ParlayOptimizer()
    optimized_data = optimizer.rebuild_parlays_low_correlation(...)
  
  AFTER: Using EnhancedParlayBuilder
    from scripts.analysis.correlation_detector import EnhancedParlayBuilder
    builder = EnhancedParlayBuilder()
    enhanced_parlays = builder.build_parlays_with_correlation(
        all_analyses,
        min_confidence=65,
        max_correlation_penalty=-20.0  # Allow up to 2 strong correlations
    )

□ Step 4: Update Display Logic
  Already implemented in format_parlay_with_correlations() function
  Automatically shows:
  - Original vs. adjusted confidence
  - Correlation penalty breakdown
  - Emoji-coded correlation warnings


# ============================================================================
# KEY PARAMETERS TO TUNE
# ============================================================================

1. Correlation Strength Matrix Values (correlation_detector.py ~30-50)
   Current ranges: 0.5 (minimal) to 1.5 (very strong)
   
   Tune based on actual results:
   - If DVOA+Matchup correlations fail more than expected → increase to 1.6+
   - If weak correlations (0.5-0.7) fail less than expected → decrease to 0.4

2. Penalty Scale (-5.0 multiplier)
   Current: penalty = -5.0 * strength
   
   Adjust if all correlations are too harsh or too lenient:
   - Too harsh: reduce to -4.0
   - Too lenient: increase to -6.0
   - Change uniformly affects all correlation types equally

3. Max Correlation Penalty (build_parlays_with_correlation param)
   Current: -20.0% maximum
   
   Controls how much a single parlay can be penalized:
   - -10%: Conservative (catches 2 weak correlations)
   - -20%: Moderate (allows 2-3 strong correlations)
   - -30%: Aggressive (only punishes extreme cases)


# ============================================================================
# UNDERSTANDING THE OUTPUT
# ============================================================================

Sample Output:

PARLAY 3 - MODERATE RISK
Combined Confidence: 68% (was 76%, -8% correlation penalty)
EV: +2.3%
Recommended Bet: 0.5 units

  Leg 1: Patrick Mahomes (KC)
         PASS YARDS OVER 280
         vs LV | Confidence: 72%
         [driven by DVOA, Volume]
  
  Leg 2: Travis Kelce (KC)
         REC YARDS OVER 65
         vs LV | Confidence: 72%
         [driven by DVOA, Matchup]
  
  Leg 3: Christian McCaffrey (SF)
         RUSH YARDS OVER 85
         vs NO | Confidence: 58%
         [driven by Trend, Volume]

  Rationale:
    • All three legs capitalize on weak defenses through different stat types

  📊 Correlation Analysis:
    • 🔥 Mahomes (KC) & Kelce (KC): both driven by DVOA + Matchup
    • ⚡ Kelce (KC) & McCaffrey (SF): share Volume driver

INTERPRETATION:
  1. Emoji tells story: 🔥 means red flag, ⚠️ means caution, ⚡ means minor
  2. Confidence dropped 8% due to DVOA+Matchup pair (very strong correlation)
  3. The system is saying: "KC passing game is correlated, be aware"
  4. EV still positive (2.3%), so if you believe in the edge, reasonable to bet


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

ISSUE: All parlays showing -20% correlation penalty
DIAGNOSIS: Likely error in driver extraction
FIX: Check that top_contributing_agents is being populated correctly
     Run: python debug_agents.py to verify agent scores

ISSUE: No correlation warnings appearing
DIAGNOSIS: Shared drivers not being detected
FIX: Verify agents are using consistent names (all caps, exact spelling)
     Check: (['DVOA'] not ['dvoa'] or ['dvoa_agent'])

ISSUE: Penalties seem too harsh/too lenient
DIAGNOSIS: Strength matrix values need tuning
FIX: Run test_correlation_strength_matrix.py with sample data
     Compare to actual parlay results from past weeks
     Document why you're adjusting specific values

ISSUE: EnhancedParlayBuilder not working with existing code
DIAGNOSIS: Import path or interface mismatch
FIX: Ensure correlation_detector.py is in scripts/analysis/
     Verify it can import from .parlay_builder
     Check that PropAnalysis model matches expected structure


# ============================================================================
# NEXT STEPS & FUTURE IMPROVEMENTS
# ============================================================================

SHORT TERM (This Week):
  1. Run test suite to validate
  2. Test with sample parlay generation
  3. Compare output to expectations from last chat
  4. Integrate into betting CLI

MEDIUM TERM (Next 2-3 Weeks):
  1. Track actual results of correlated vs uncorrelated parlays
  2. Gather calibration data for strength matrix refinement
  3. Adjust strength values based on real performance
  4. Consider position-specific correlation rules (WR vs RB)

LONG TERM (Post Season):
  1. Full backtesting of correlation accuracy
  2. Statistical analysis of whether strength matrix is predictive
  3. Potential expansion: correlation by game (same game parlays)
  4. Time-based adjustments (early vs late season dynamics)


# ============================================================================
# FILES CHANGED / CREATED
# ============================================================================

✓ Modified: scripts/analysis/correlation_detector.py
  - Rewrote correlation strength matrix
  - Fixed penalty calculation logic
  - Added safe driver extraction method
  - Improved warning generation
  - Better emoji/strength mapping

✓ Created: test_correlation_strength_matrix.py
  - Comprehensive test suite
  - Validation for all penalty calculations
  - Calibration guide
  - Ready to run immediately

Files NOT changed (shouldn't need to be):
  - parlay_builder.py: Still works as-is
  - betting_cli_with_live_odds.py: Can use either old or new approach
  - models.py: Prop/Parlay models unchanged


# ============================================================================
# QUICK START
# ============================================================================

To see it in action:

1. Run the test suite:
   $ python test_correlation_strength_matrix.py
   
2. Look for the 5 tests:
   TEST 1: Strength matrix values (should all show ✓)
   TEST 2: Penalty calculations (should match expected)
   TEST 3: Emoji indicators (visual validation)
   TEST 4: Full parlay analysis (complex case)
   TEST 5: High confidence protection (proves it doesn't over-penalize)

3. If all tests pass: System is ready for integration
4. If tests fail: Debug using the Troubleshooting section above


# ============================================================================
# VALIDATION CRITERIA
# ============================================================================

System is working correctly when:

✓ DVOA + Matchup pairs get -7.5% penalty (not -10%)
✓ Volume + Trend pairs get -3.5% penalty (not -10%)
✓ Parlays with no shared drivers show 0% correlation penalty
✓ Warnings include emoji (🔥 ⚠️ ⚡) indicating strength
✓ High-confidence parlays (70%+) still make sense after penalty
✓ Test suite runs without errors
✓ Output clearly explains which agents are driving correlation


Made with 🔧 by Scott's NFL Betting System
Dynamic Correlation Detection | November 2025
"""
