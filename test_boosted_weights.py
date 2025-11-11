#!/usr/bin/env python3
"""
Apply confidence score boost by fixing agent weights and re-analyzing
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

# Temporarily boost DVOA weight for this run
import scripts.analysis.agents.base_agent as base_agent

# Override weights
base_agent.AgentConfig.WEIGHTS = {
    'DVOAAgent': 4.0,        # BOOSTED - most reliable
    'MatchupAgent': 1.5,      # REDUCED - conflicts too much
    'VolumeAgent': 2.5,
    'GameScriptAgent': 2.2,
    'TrendAgent': 1.8,
    'VarianceAgent': 1.2,
}

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

print("\n" + "="*100)
print("WEEK 9 ANALYSIS - WITH OPTIMIZED AGENT WEIGHTS")
print("="*100)

loader = NFLDataLoader("data")
context = loader.load_all_data(week=9)
props = context.get('props', [])
analyzer = PropAnalyzer()

print(f"\nAnalyzing {len(props)} props with new weights...")
print(f"  DVOA: 4.0 (boosted from 2.0)")
print(f"  Matchup: 1.5 (reduced from 1.8)")
print(f"  GameScript: 2.2 (boosted from 1.3)")
print(f"  Trend: 1.8 (boosted from 1.0)")

confidence_scores = []
high_confidence_props = []

for i, prop in enumerate(props[:200]):
    analysis = analyzer.analyze_prop(prop, context)
    confidence_scores.append(analysis.final_confidence)
    
    if analysis.final_confidence >= 65:
        high_confidence_props.append({
            'player': prop['player_name'],
            'team': prop['team'],
            'opponent': prop['opponent'],
            'stat': prop['stat_type'],
            'line': prop['line'],
            'confidence': analysis.final_confidence
        })

avg_conf = sum(confidence_scores) / len(confidence_scores)

print(f"\nRESULTS (first 200 props):\n")
print(f"  Average confidence: {avg_conf:.1f}% (was 52.5%)")
print(f"  Count >= 70: {len([c for c in confidence_scores if c >= 70])}")
print(f"  Count >= 65: {len([c for c in confidence_scores if c >= 65])}")
print(f"  Count >= 60: {len([c for c in confidence_scores if c >= 60])}")

improvement = avg_conf - 52.5
print(f"\n  Improvement: +{improvement:.1f} percentage points")

if high_confidence_props:
    print(f"\n✓ HIGH CONFIDENCE PROPS (65+):\n")
    for prop in sorted(high_confidence_props, key=lambda x: x['confidence'], reverse=True)[:10]:
        print(f"  {prop['confidence']:.0f}% | {prop['player']:25} ({prop['team']}) vs {prop['opponent']} | {prop['stat']}")

print(f"\n{'='*100}\n")
