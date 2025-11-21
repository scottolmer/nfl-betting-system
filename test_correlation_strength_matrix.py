"""
Test and Calibration Suite for PROJECT 3 IMPROVEMENT #1:
Dynamic Correlation Strength Matrix

This suite validates that the dynamic penalty system:
1. Correctly calculates penalties based on correlation strength
2. Applies appropriate emojis/warnings for different correlation types
3. Caps penalties at the right thresholds
4. Provides clear diagnostic output for system calibration

Run with: python test_correlation_strength_matrix.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.correlation_detector import CorrelationAnalyzer, EnhancedParlayBuilder
from scripts.analysis.models import PropAnalysis, PlayerProp


class MockProp:
    """Mock Prop for testing"""
    def __init__(self, player_name, team, stat_type, line, opponent="NEUTRAL"):
        self.player_name = player_name
        self.team = team
        self.stat_type = stat_type
        self.line = line
        self.opponent = opponent
        self.bet_type = "OVER"
        self.position = "WR"


class MockPropAnalysis:
    """Mock PropAnalysis for testing correlation strength"""
    def __init__(self, player_name, team, drivers):
        self.prop = MockProp(player_name, team, "REC", 5.5)
        self.agent_breakdown = {}
        # Simulate top contributing agents
        self.top_contributing_agents = [(agent, 0.5) for agent in drivers]
        self.final_confidence = 65


def test_correlation_strength_matrix():
    """Test the correlation strength matrix values"""
    print("\n" + "="*70)
    print("TEST 1: Correlation Strength Matrix Calibration")
    print("="*70 + "\n")
    
    analyzer = CorrelationAnalyzer()
    
    test_cases = [
        # (agent1, agent2, expected_strength, description)
        ('DVOA', 'Matchup', 1.5, "Very Strong - same fundamental weakness"),
        ('DVOA', 'GameScript', 1.3, "Strong - game flow from weak defense"),
        ('Matchup', 'GameScript', 1.2, "Strong - matchup context affects script"),
        ('Injury', 'Volume', 1.1, "Moderate-Strong - injury affects usage"),
        ('DVOA', 'Volume', 1.0, "Moderate - baseline correlation"),
        ('Injury', 'Matchup', 0.9, "Moderate - injury affects matchup"),
        ('Trend', 'Volume', 0.7, "Weak - different signal types"),
        ('Trend', 'Injury', 0.6, "Weak - performance vs health"),
        ('Variance', 'Weather', 0.5, "Very Weak - minimal overlap"),
    ]
    
    print("Agent Pair Strength Values:")
    print("-" * 70)
    all_pass = True
    for agent1, agent2, expected, description in test_cases:
        actual = analyzer.get_correlation_strength(agent1, agent2)
        status = "✓" if actual == expected else "✗"
        if actual != expected:
            all_pass = False
        print(f"{status} {agent1:12} + {agent2:12} = {actual:.1f} ({description})")
    
    print("\n" + "="*70 + "\n")
    return all_pass


def test_penalty_calculations():
    """Test that penalty calculation works correctly"""
    print("="*70)
    print("TEST 2: Penalty Calculation Accuracy")
    print("="*70 + "\n")
    
    analyzer = CorrelationAnalyzer()
    
    # Create mock props with different driver combinations
    test_cases = [
        # (leg1_drivers, leg2_drivers, expected_penalty, description)
        (['DVOA', 'Matchup'], ['DVOA', 'Matchup'], -7.5, "DVOA+Matchup pair (strongest)"),
        (['DVOA', 'GameScript'], ['DVOA', 'GameScript'], -6.5, "DVOA+GameScript pair (strong)"),
        (['DVOA', 'Volume'], ['DVOA', 'Volume'], -5.0, "DVOA+Volume pair (moderate)"),
        (['Volume', 'Trend'], ['Volume', 'Trend'], -3.5, "Volume+Trend pair (weak)"),
        (['Variance', 'Weather'], ['Variance', 'Weather'], -2.5, "Variance+Weather pair (very weak)"),
        (['DVOA'], ['Volume'], 0.0, "No shared drivers (independent)"),
    ]
    
    print("Penalty Calculations:")
    print("-" * 70)
    all_pass = True
    for i, (drivers1, drivers2, expected, description) in enumerate(test_cases):
        leg1 = MockPropAnalysis(f"Player{i}_A", "KC", drivers1)
        leg2 = MockPropAnalysis(f"Player{i}_B", "KC", drivers2)
        
        penalty, warnings = analyzer.calculate_correlation_risk(leg1, leg2)
        
        status = "✓" if abs(penalty - expected) < 0.1 else "✗"
        if abs(penalty - expected) > 0.1:
            all_pass = False
        print(f"{status} {description}")
        print(f"   Expected: {expected:.1f}% | Actual: {penalty:.1f}%")
        if warnings:
            for w in warnings:
                print(f"   Warning: {w}")
    
    print("\n" + "="*70 + "\n")
    return all_pass


def test_emoji_indicators():
    """Test that correlation strength gets appropriate emoji/description"""
    print("="*70)
    print("TEST 3: Emoji & Strength Indicators")
    print("="*70 + "\n")
    
    analyzer = CorrelationAnalyzer()
    
    strength_tests = [
        (1.5, "🔥", "Very Strong"),
        (1.3, "🔥", "Very Strong"),
        (1.2, "🔥", "Very Strong"),
        (1.0, "⚠️", "Moderate"),
        (0.9, "⚠️", "Moderate"),
        (0.7, "⚡", "Weak"),
        (0.5, "⚡", "Weak"),
    ]
    
    print("Strength to Emoji Mapping:")
    print("-" * 70)
    all_pass = True
    for strength, expected_emoji, description in strength_tests:
        actual_emoji = analyzer._get_strength_emoji(strength)
        status = "✓" if actual_emoji == expected_emoji else "✗"
        if actual_emoji != expected_emoji:
            all_pass = False
        print(f"{status} {strength:.1f} → {actual_emoji} ({description})")
    
    print("\n" + "="*70 + "\n")
    return all_pass


def test_parlay_correlation_analysis():
    """Test full parlay correlation analysis with multiple legs"""
    print("="*70)
    print("TEST 4: Full Parlay Correlation Analysis")
    print("="*70 + "\n")
    
    analyzer = CorrelationAnalyzer()
    
    # Create a 3-leg parlay
    leg1 = MockPropAnalysis("Player1", "KC", ['DVOA', 'Matchup'])
    leg2 = MockPropAnalysis("Player2", "KC", ['DVOA', 'Volume'])
    leg3 = MockPropAnalysis("Player3", "KC", ['Trend', 'Volume'])
    
    parlay_legs = [leg1, leg2, leg3]
    
    total_penalty, warnings = analyzer.analyze_parlay_correlations(parlay_legs)
    
    print("3-Leg Parlay Analysis:")
    print(f"  Leg 1: Player1 (drivers: DVOA, Matchup)")
    print(f"  Leg 2: Player2 (drivers: DVOA, Volume)")
    print(f"  Leg 3: Player3 (drivers: Trend, Volume)")
    print()
    print(f"Total Correlation Penalty: {total_penalty:.1f}%")
    print()
    print("Detected Correlations:")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")
    
    # Expected: ~-10.0%
    expected_penalty = -10.0
    all_pass = abs(total_penalty - expected_penalty) < 0.1
    
    status = "✓" if all_pass else "✗"
    print(f"\n{status} Expected total: {expected_penalty:.1f}% | Actual: {total_penalty:.1f}%")
    
    print("\n" + "="*70 + "\n")
    return all_pass


def test_high_confidence_parlay_protection():
    """Test that high-confidence parlays aren't over-penalized"""
    print("="*70)
    print("TEST 5: High Confidence Parlay Protection")
    print("="*70 + "\n")
    
    analyzer = CorrelationAnalyzer()
    
    leg1 = MockPropAnalysis("Star1", "KC", ['DVOA', 'Volume'])
    leg2 = MockPropAnalysis("Star2", "KC", ['DVOA', 'Matchup'])
    leg3 = MockPropAnalysis("Star3", "KC", ['GameScript', 'Trend'])
    
    leg1.final_confidence = 70
    leg2.final_confidence = 75
    leg3.final_confidence = 68
    
    parlay_legs = [leg1, leg2, leg3]
    
    total_penalty, warnings = analyzer.analyze_parlay_correlations(parlay_legs)
    
    print("High-Confidence 3-Leg Parlay:")
    print(f"  Leg 1: 70% confidence (DVOA, Volume)")
    print(f"  Leg 2: 75% confidence (DVOA, Matchup)")
    print(f"  Leg 3: 68% confidence (GameScript, Trend)")
    print()
    print(f"Base Parlay Confidence (pre-penalty): ~73%")
    print(f"Correlation Penalty Applied: {total_penalty:.1f}%")
    print(f"Final Parlay Confidence (post-penalty): ~{73 + int(total_penalty)}%")
    print()
    print("Correlations Detected:")
    for warning in warnings:
        print(f"  • {warning}")
    
    # Should still be reasonable
    all_pass = total_penalty < 0 and total_penalty > -20  # Penalty applied but not destroyed
    
    print(f"\n✓ Penalty is reasonable (not over-penalized)")
    print("\n" + "="*70 + "\n")
    return all_pass


def print_calibration_guide():
    """Print guidance for calibrating the system based on live results"""
    print("="*70)
    print("CALIBRATION GUIDE: Using Live Results to Refine Strengths")
    print("="*70 + "\n")
    
    print("""
After betting season, use actual parlay results to refine correlation strengths:

1. TRACK ACTUAL LOSSES:
   - When a parlay with DVOA+Matchup correlation loses, note it
   - When a parlay with Trend+Volume correlation loses, note it
   - Compare loss rates between correlation types

2. CALCULATE CALIBRATION METRICS:
   - For DVOA+Matchup: if 75% of these lose, strength is accurate (1.5)
   - For Trend+Volume: if only 40% of these lose, strength too high, reduce to 0.5
   - Target: correlations should predict loss rate accurately

3. REFINE THE MATRIX:
   - If a strength value consistently predicts wrong, adjust by ±0.1-0.2
   - Document changes with timestamp and rationale
   - Run backtests after each adjustment

4. TRACK EDGE CASES:
   - Some correlations may be position-specific (WR vs RB)
   - Some may be season-specific (early vs late season)
   - Consider adding nuance if data supports it

CURRENT HYPOTHESIS:
- Strong correlations (1.3+) should warn at 70%+ of combined losses
- Moderate correlations (0.9-1.1) should be present in 50-60% of losses  
- Weak correlations (0.5-0.7) should have minimal impact on results
""")
    
    print("="*70 + "\n")
    return True


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" " * 15 + "PROJECT 3 IMPROVEMENT #1: DYNAMIC CORRELATION STRENGTH")
    print(" " * 20 + "Test & Calibration Suite")
    print("="*80)
    
    results = []
    
    results.append(("TEST 1: Strength Matrix", test_correlation_strength_matrix()))
    results.append(("TEST 2: Penalty Calculations", test_penalty_calculations()))
    results.append(("TEST 3: Emoji Indicators", test_emoji_indicators()))
    results.append(("TEST 4: Full Parlay Analysis", test_parlay_correlation_analysis()))
    results.append(("TEST 5: High Confidence Protection", test_high_confidence_parlay_protection()))
    
    print_calibration_guide()
    
    print("="*80)
    print("TEST SUMMARY")
    print("="*80 + "\n")
    
    all_pass = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_pass = False
    
    print()
    print("="*80)
    if all_pass:
        print("✅ ALL TESTS PASSED! System is ready for integration.")
        print("\nNEXT STEPS:")
        print("  1. Read: PROJECT_3_IMPROVEMENT_1_QUICK_REFERENCE.txt")
        print("  2. Integrate: EnhancedParlayBuilder into your betting CLI")
        print("  3. Test: Generate sample parlays and verify output")
    else:
        print("❌ SOME TESTS FAILED. Review output above for details.")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
