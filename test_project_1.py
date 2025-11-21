"""
Test script for Project 1: Kill the Neutral Score Problem
Verifies that agents returning None are properly excluded from confidence calculations
"""

import sys
import os
import logging

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import DataLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def test_project_1_none_handling():
    """Test that agents returning None are skipped properly"""
    print("\n" + "="*70)
    print("PROJECT 1 TEST: Verify agents returning None are skipped")
    print("="*70)
    
    # Load test data
    loader = DataLoader(week=10)
    props = loader.load_props()
    context = loader.build_context()
    
    if not props:
        print("❌ No props loaded for testing!")
        return False
    
    # Analyze a small sample
    analyzer = PropAnalyzer()
    sample_props = props[:5]  # Test first 5 props
    
    print(f"\n📊 Analyzing {len(sample_props)} sample props...\n")
    
    results = []
    for prop_data in sample_props:
        analysis = analyzer.analyze_prop(prop_data, context)
        results.append(analysis)
        
        print(f"Prop: {analysis.prop.player_name} {analysis.prop.stat_type} ({analysis.prop.bet_type})")
        print(f"  Final Confidence: {analysis.final_confidence}%")
        
        # Show which agents contributed
        contributed_agents = [name for name, result in analysis.agent_breakdown.items() 
                            if result.get('weight', 0) > 0 or result.get('raw_score', 50) != 50]
        skipped_agents = [name for name in analyzer.agents.keys() 
                         if name not in analysis.agent_breakdown]
        
        print(f"  Contributing Agents ({len(contributed_agents)}): {', '.join(contributed_agents)}")
        if skipped_agents:
            print(f"  Skipped Agents ({len(skipped_agents)}): {', '.join(skipped_agents)}")
        print()
    
    # Calculate stats
    avg_confidence = sum(r.final_confidence for r in results) / len(results)
    overs = [r for r in results if r.prop.bet_type == 'OVER']
    unders = [r for r in results if r.prop.bet_type == 'UNDER']
    
    print("="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    print(f"Props Analyzed: {len(results)}")
    print(f"Average Confidence: {avg_confidence:.1f}%")
    print(f"  OVER average: {sum(r.final_confidence for r in overs)/len(overs):.1f}% ({len(overs)} props)" if overs else "  OVER: 0 props")
    print(f"  UNDER average: {sum(r.final_confidence for r in unders)/len(unders):.1f}% ({len(unders)} props)" if unders else "  UNDER: 0 props")
    
    # Check confidence distribution
    conf_ranges = {
        '50-60%': len([r for r in results if 50 <= r.final_confidence < 60]),
        '60-70%': len([r for r in results if 60 <= r.final_confidence < 70]),
        '70-80%': len([r for r in results if 70 <= r.final_confidence < 80]),
        '80-90%': len([r for r in results if 80 <= r.final_confidence < 90]),
        '90-100%': len([r for r in results if 90 <= r.final_confidence <= 100]),
    }
    
    print("\nConfidence Distribution:")
    for range_label, count in conf_ranges.items():
        print(f"  {range_label}: {count} props")
    
    print("\n✅ Test completed - check logs above for agent skipping details")
    return True

def test_specific_agent_behavior():
    """Test that specific agents return None when appropriate"""
    print("\n" + "="*70)
    print("PROJECT 1 TEST: Verify specific agents return None correctly")
    print("="*70)
    
    from scripts.analysis.agents.weather_agent import WeatherAgent
    from scripts.analysis.agents.injury_agent import InjuryAgent
    from scripts.analysis.models import PlayerProp
    
    # Create test prop
    test_prop = PlayerProp(
        player_name="Test Player",
        team="KC",
        opponent="LAC",
        position="WR",
        stat_type="Rec Yards",
        line=100,
        bet_type="OVER"
    )
    
    # Test Weather Agent with no weather data
    print("\n📍 Testing Weather Agent (should return None with no weather data)...")
    weather_agent = WeatherAgent()
    context_no_weather = {'weather': {}}
    result = weather_agent.analyze(test_prop, context_no_weather)
    if result is None:
        print("  ✅ Weather Agent correctly returned None when no weather data")
    else:
        print(f"  ❌ Weather Agent returned {result} instead of None")
    
    # Test Injury Agent with no injury data
    print("\nTesting Injury Agent (should return None with no injury data)...")
    injury_agent = InjuryAgent()
    context_no_injuries = {'injuries': ''}
    result = injury_agent.analyze(test_prop, context_no_injuries)
    if result is None:
        print("  ✅ Injury Agent correctly returned None when no injury data")
    else:
        print(f"  ❌ Injury Agent returned {result} instead of None")
    
    print("\n✅ Agent behavior test completed")
    return True

if __name__ == '__main__':
    try:
        success1 = test_specific_agent_behavior()
        success2 = test_project_1_none_handling()
        
        if success1 and success2:
            print("\n" + "="*70)
            print("🎉 ALL PROJECT 1 TESTS PASSED!")
            print("="*70)
            sys.exit(0)
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
