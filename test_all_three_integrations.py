#!/usr/bin/env python
"""Test all three new Claude integrations"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

print("\n" + "="*70)
print("🏈 TESTING THREE NEW CLAUDE INTEGRATIONS")
print("="*70 + "\n")

# Test 1: Weather Analyzer
print("1️⃣  WEATHER IMPACT ANALYZER")
print("-" * 70)
try:
    from scripts.analysis.weather_analyzer import WeatherImpactAnalyzer
    
    weather_analyzer = WeatherImpactAnalyzer()
    
    weather_data = {
        'conditions': 'Heavy snow',
        'temp_f': 25,
        'wind_mph': 20,
        'wind_direction': 'NW',
        'precipitation_chance': 90,
        'forecast': 'Snow through halftime'
    }
    
    result = weather_analyzer.analyze_weather_impact("GB", "CHI", "Pass Yds", weather_data)
    print(f"✅ Weather analysis complete")
    print(f"   Passing impact: {result['passing_impact']:+d}")
    print(f"   Rushing impact: {result['rushing_impact']:+d}")
    print(f"   Overall adjustment: {result['overall_adjustment']:+d}")
    print(f"   Reasoning: {result['reasoning']}\n")
except Exception as e:
    print(f"❌ Weather analyzer failed: {e}\n")

# Test 2: CSV Normalizer
print("2️⃣  CSV NORMALIZER")
print("-" * 70)
try:
    from scripts.analysis.csv_normalizer import CSVNormalizer
    
    normalizer = CSVNormalizer()
    
    players = ["jordan love", "J.Love", "Love, Jordan", "Jaylen Waddle", "J. Waddle"]
    mappings = normalizer.normalize_player_names(players)
    print(f"✅ Player name normalization complete")
    for orig, norm in list(mappings.items())[:3]:
        print(f"   '{orig}' → '{norm}'")
    
    stats = ["Pass Yds", "PassYards", "pass yards", "Rush Yards", "rec_yds"]
    validation = normalizer.validate_stat_types(stats)
    print(f"\n✅ Stat validation complete")
    print(f"   Issues found: {len(validation.get('issues', []))}")
    print(f"   Categories identified: {len(validation.get('categories', {}))}\n")
except Exception as e:
    print(f"❌ CSV normalizer failed: {e}\n")

# Test 3: Agent Calibrator
print("3️⃣  AGENT CALIBRATOR")
print("-" * 70)
try:
    from scripts.analysis.agent_calibrator import AgentCalibrator
    
    calibrator = AgentCalibrator()
    
    sample_perf = {
        'DVOA': [
            {'confidence': 70, 'prediction': 'OVER', 'actual': 'OVER', 'hit': True},
            {'confidence': 65, 'prediction': 'UNDER', 'actual': 'OVER', 'hit': False},
            {'confidence': 75, 'prediction': 'OVER', 'actual': 'OVER', 'hit': True},
        ],
        'Matchup': [
            {'confidence': 60, 'prediction': 'OVER', 'actual': 'OVER', 'hit': True},
            {'confidence': 55, 'prediction': 'UNDER', 'actual': 'UNDER', 'hit': True},
        ],
    }
    
    analysis = calibrator.analyze_agent_performance(sample_perf)
    print(f"✅ Agent performance analysis complete")
    print(f"   Top performers: {analysis.get('top_performers', [])}")
    print(f"   Needs improvement: {analysis.get('needs_improvement', [])}")
    print(f"   Recommended adjustments: {bool(analysis.get('weight_recommendations', {}))}\n")
except Exception as e:
    print(f"❌ Agent calibrator failed: {e}\n")

# Test 4: Integrated Query Handler
print("4️⃣  INTEGRATED CLAUDE QUERY HANDLER")
print("-" * 70)
try:
    from scripts.api.claude_query_handler import ClaudeQueryHandler
    
    handler = ClaudeQueryHandler()
    
    weather = {
        'conditions': 'Cloudy',
        'temp_f': 42,
        'wind_mph': 8,
        'humidity_pct': 65
    }
    
    response = handler.query("Jordan Love 250 pass yards", week=9, weather=weather)
    print(f"✅ Full integration test complete\n")
    print("="*70)
    print(response)
    print("="*70 + "\n")
except Exception as e:
    print(f"❌ Integrated handler failed: {e}\n")
    import traceback
    traceback.print_exc()

print("✅ ALL INTEGRATIONS TESTED\n")
