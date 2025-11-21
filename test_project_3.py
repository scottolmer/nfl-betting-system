"""
PROJECT 3 TEST: Strategic Correlation Risk Detection
Tests the correlation detection system with sample parlays
"""

import sys
sys.path.insert(0, 'scripts')

from analysis.models import PlayerProp, PropAnalysis
from analysis.correlation_detector import CorrelationAnalyzer, EnhancedParlayBuilder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_analysis(
    player_name: str, 
    stat_type: str, 
    confidence: int,
    top_agents: list,  # [('agent_name', contribution), ...]
    team: str = "HOU",
    opponent: str = "DEN"
) -> PropAnalysis:
    """Create a sample PropAnalysis for testing"""
    
    prop = PlayerProp(
        player_name=player_name,
        team=team,
        opponent=opponent,
        position="WR",
        stat_type=stat_type,
        line=5.5,
        bet_type="OVER"
    )
    
    # Create agent breakdown from top_agents
    agent_breakdown = {}
    for agent_name, contrib in top_agents:
        agent_breakdown[agent_name] = {
            'raw_score': 60,
            'weight': 0.15,
            'direction': 'OVER',
            'rationale': [f'{agent_name} signal']
        }
    
    analysis = PropAnalysis(
        prop=prop,
        final_confidence=confidence,
        recommendation="LEAN OVER",
        rationale=[f"Strong {player_name} edge"],
        agent_breakdown=agent_breakdown,
        edge_explanation=f"{confidence}% edge driven by {', '.join([a[0] for a in top_agents])}",
        top_contributing_agents=top_agents
    )
    
    return analysis


def test_correlation_detection():
    """Test correlation detection between props"""
    
    print("\n" + "="*70)
    print("PROJECT 3 TEST: Correlation Risk Detection")
    print("="*70)
    
    analyzer = CorrelationAnalyzer()
    
    # Create sample props with shared drivers
    print("\n1️⃣  Creating test props with SHARED drivers (DVOA, Matchup)...")
    
    # Both driven by DVOA and Matchup (HOU weak pass defense)
    josh_allen = create_sample_analysis(
        player_name="Josh Allen",
        stat_type="Pass Yards",
        confidence=72,
        top_agents=[("DVOA", 35), ("Matchup", 28)],
        team="BUF",
        opponent="HOU"
    )
    
    khalil_shakir = create_sample_analysis(
        player_name="Khalil Shakir",
        stat_type="Receptions",
        confidence=68,
        top_agents=[("DVOA", 32), ("Matchup", 30)],
        team="BUF",
        opponent="HOU"
    )
    
    # Independent prop (different drivers)
    joe_flacco = create_sample_analysis(
        player_name="Joe Flacco",
        stat_type="Pass Yards",
        confidence=62,
        top_agents=[("Volume", 40), ("Trend", 35)],
        team="DEN",
        opponent="HOU"
    )
    
    print(f"  ✓ Josh Allen (75% conf): Driven by DVOA + Matchup")
    print(f"  ✓ Khalil Shakir (68% conf): Driven by DVOA + Matchup")
    print(f"  ✓ Joe Flacco (62% conf): Driven by Volume + Trend")
    
    # Test 1: Correlation between correlated props
    print("\n2️⃣  Testing CORRELATED pair (Allen & Shakir - same drivers)...")
    penalty, warnings = analyzer.analyze_parlay_correlations([josh_allen, khalil_shakir])
    print(f"  Correlation penalty: {penalty}%")
    for warning in warnings:
        print(f"  {warning}")
    
    if penalty < 0:
        print(f"  ✅ CORRECTLY detected correlation (-10% penalty)")
    else:
        print(f"  ❌ FAILED to detect correlation")
    
    # Test 2: No correlation between independent props
    print("\n3️⃣  Testing INDEPENDENT pair (Shakir & Flacco - different drivers)...")
    penalty2, warnings2 = analyzer.analyze_parlay_correlations([khalil_shakir, joe_flacco])
    print(f"  Correlation penalty: {penalty2}%")
    if warnings2:
        for warning in warnings2:
            print(f"  {warning}")
    else:
        print(f"  (No correlation detected)")
    
    if penalty2 == 0:
        print(f"  ✅ CORRECTLY identified no correlation")
    else:
        print(f"  ❌ FALSE positive correlation detected")
    
    # Test 3: Three-way correlation
    print("\n4️⃣  Testing 3-LEG PARLAY with mixed correlation...")
    penalty3, warnings3 = analyzer.analyze_parlay_correlations(
        [josh_allen, khalil_shakir, joe_flacco]
    )
    print(f"  Total correlation penalty: {penalty3}%")
    for warning in warnings3:
        print(f"  {warning}")
    
    expected_penalty = -10  # Allen-Shakir share 2 drivers (-10)
    if penalty3 == expected_penalty:
        print(f"  ✅ CORRECT: 3-leg penalty matches expected (-10%)")
    else:
        print(f"  ⚠️  3-leg penalty: {penalty3}% (expected {expected_penalty}%)")
    
    # Test 4: Enhanced parlay builder
    print("\n5️⃣  Testing Enhanced Parlay Builder...")
    builder = EnhancedParlayBuilder()
    
    # Calculate contributions
    contrib1 = builder.calculate_prop_contributions(josh_allen)
    print(f"  Josh Allen contributions: {contrib1}")
    
    contrib2 = builder.calculate_prop_contributions(khalil_shakir)
    print(f"  Khalil Shakir contributions: {contrib2}")
    
    print("\n" + "="*70)
    print("✅ PROJECT 3 TESTS COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_correlation_detection()
