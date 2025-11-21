#!/usr/bin/env python
"""
Debug script to trace agent scoring for OVER vs UNDER props
"""

import sys
from pathlib import Path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader

print("=" * 90)
print("Debugging Agent Scoring for OVER vs UNDER")
print("=" * 90)

# Load data
loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=12)

props = context.get('props', [])
print(f"\nLoaded {len(props)} props")

# Group by player/stat/line to find OVER/UNDER pairs
player_stat_line_combos = {}
for prop in props:
    key = (prop['player_name'], prop['stat_type'], prop['line'])
    if key not in player_stat_line_combos:
        player_stat_line_combos[key] = {'OVER': None, 'UNDER': None}
    
    bet_type = 'UNDER' if prop.get('bet_type', '').lower() == 'under' else 'OVER'
    player_stat_line_combos[key][bet_type] = prop

# Find a pair with BOTH OVER and UNDER
test_pair = None
for combo, bets in player_stat_line_combos.items():
    if bets['OVER'] and bets['UNDER']:
        test_pair = combo
        break

if not test_pair:
    print("❌ No matching OVER/UNDER pairs found")
    sys.exit(1)

over_prop = player_stat_line_combos[test_pair]['OVER']
under_prop = player_stat_line_combos[test_pair]['UNDER']

print(f"\n{'='*90}")
print(f"Testing: {over_prop['player_name']} - {over_prop['stat_type']} @ {over_prop['line']}")
print(f"{'='*90}")

# Analyze both
analyzer = PropAnalyzer()

print(f"\nAnalyzing OVER bet...")
over_analysis = analyzer.analyze_prop(over_prop, context)
print(f"  Bet Type in Prop: {over_analysis.prop.bet_type}")
print(f"  Final Confidence: {over_analysis.final_confidence}%")
print(f"  Agent Breakdown:")
for agent in sorted(over_analysis.agent_breakdown.keys()):
    result = over_analysis.agent_breakdown[agent]
    print(f"    {agent:15s}: {result['raw_score']:5.1f}% (weight={result['weight']:.1f})")

print(f"\nAnalyzing UNDER bet...")
under_analysis = analyzer.analyze_prop(under_prop, context)
print(f"  Bet Type in Prop: {under_analysis.prop.bet_type}")
print(f"  Final Confidence: {under_analysis.final_confidence}%")
print(f"  Agent Breakdown:")
for agent in sorted(under_analysis.agent_breakdown.keys()):
    result = under_analysis.agent_breakdown[agent]
    print(f"    {agent:15s}: {result['raw_score']:5.1f}% (weight={result['weight']:.1f})")

print(f"\n{'='*90}")
print("COMPARISON:")
print(f"{'='*90}")
print(f"OVER:  {over_analysis.final_confidence}%")
print(f"UNDER: {under_analysis.final_confidence}%")
print(f"Difference: {over_analysis.final_confidence - under_analysis.final_confidence}%")

# Check if inversion is working
print(f"\nInversion Check (OVER + UNDER should = 100):")
over_avg = sum(r['raw_score'] for r in over_analysis.agent_breakdown.values()) / len(over_analysis.agent_breakdown)
under_avg = sum(r['raw_score'] for r in under_analysis.agent_breakdown.values()) / len(under_analysis.agent_breakdown)

print(f"  Average agent score (OVER): {over_avg:.1f}%")
print(f"  Average agent score (UNDER): {under_avg:.1f}%")
print(f"  Sum: {over_avg + under_avg:.1f}%")

if abs((over_avg + under_avg) - 100) < 2:
    print("  ✅ Inversion is working!")
else:
    print(f"  ⚠️  Sum is {over_avg + under_avg:.1f}% (expected ~100%)")

# Check individual agents
print(f"\nAgent-by-Agent Inversion:")
for agent in sorted(over_analysis.agent_breakdown.keys()):
    over_score = over_analysis.agent_breakdown[agent]['raw_score']
    under_score = under_analysis.agent_breakdown[agent]['raw_score']
    sum_scores = over_score + under_score
    
    if abs(sum_scores - 100) < 1:
        status = "✅"
    elif abs(sum_scores - 100) < 3:
        status = "⚠️"
    else:
        status = "❌"
    
    print(f"  {agent:15s}: OVER={over_score:5.1f}% + UNDER={under_score:5.1f}% = {sum_scores:6.1f}% {status}")

# Check weights
print(f"\nWeight Check:")
over_weights = [r['weight'] for r in over_analysis.agent_breakdown.values()]
under_weights = [r['weight'] for r in under_analysis.agent_breakdown.values()]

if over_weights == under_weights:
    print("  ✅ Weights are identical")
else:
    print("  ⚠️  Weights differ!")
    for agent in sorted(over_analysis.agent_breakdown.keys()):
        ow = over_analysis.agent_breakdown[agent]['weight']
        uw = under_analysis.agent_breakdown[agent]['weight']
        if ow != uw:
            print(f"    {agent}: OVER weight={ow}, UNDER weight={uw}")
