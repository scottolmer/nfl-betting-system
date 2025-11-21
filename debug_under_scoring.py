#!/usr/bin/env python
"""
Debug script to trace agent scoring for OVER vs UNDER props
Find OVER and UNDER for same player/stat combo
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

print(f"\nLoaded {len(context.get('props', []))} props")

# Group props by player/stat/line
props_by_combo = {}
for prop in context.get('props', []):
    key = (prop['player_name'], prop['stat_type'], prop['line'])
    if key not in props_by_combo:
        props_by_combo[key] = []
    props_by_combo[key].append(prop)

# Find a combo that has BOTH OVER and UNDER
test_combo = None
for combo, bets in props_by_combo.items():
    labels = [b.get('label', 'Over').lower() for b in bets]
    if 'over' in labels and 'under' in labels:
        test_combo = combo
        break

if not test_combo:
    # If no exact line match, just find OVER and UNDER with close lines
    print("No exact line match found. Finding closest OVER/UNDER pair...")
    
    over_props = {}
    under_props = {}
    
    for prop in context.get('props', []):
        key = (prop['player_name'], prop['stat_type'])
        label = prop.get('label', 'Over').lower()
        
        if label == 'over':
            if key not in over_props:
                over_props[key] = prop
        else:
            if key not in under_props:
                under_props[key] = prop
    
    # Find common player/stat combos
    common_keys = set(over_props.keys()) & set(under_props.keys())
    
    if not common_keys:
        print("❌ No props found with both OVER and UNDER for same player/stat")
        sys.exit(1)
    
    test_key = list(common_keys)[0]
    over_prop = over_props[test_key]
    under_prop = under_props[test_key]
else:
    bets = props_by_combo[test_combo]
    over_prop = next((b for b in bets if b.get('label', 'Over').lower() == 'over'), None)
    under_prop = next((b for b in bets if b.get('label', 'Over').lower() == 'under'), None)

if not over_prop or not under_prop:
    print("❌ Could not find matching OVER/UNDER props")
    sys.exit(1)

print(f"\n{'='*90}")
print(f"Testing: {over_prop['player_name']} - {over_prop['stat_type']}")
print(f"  OVER @ {over_prop['line']}")
print(f"  UNDER @ {under_prop['line']}")
print(f"{'='*90}")

# Analyze both
analyzer = PropAnalyzer()

print(f"\nAnalyzing OVER bet...")
over_analysis = analyzer.analyze_prop(over_prop, context)
print(f"  Bet Type in Prop: {over_analysis.prop.bet_type}")
print(f"  Final Confidence: {over_analysis.final_confidence}%")
print(f"  Agent Breakdown:")
for agent, result in sorted(over_analysis.agent_breakdown.items()):
    print(f"    {agent:15s}: {result['raw_score']:5.1f}% (weight={result['weight']:.1f})")

print(f"\nAnalyzing UNDER bet...")
under_analysis = analyzer.analyze_prop(under_prop, context)
print(f"  Bet Type in Prop: {under_analysis.prop.bet_type}")
print(f"  Final Confidence: {under_analysis.final_confidence}%")
print(f"  Agent Breakdown:")
for agent, result in sorted(under_analysis.agent_breakdown.items()):
    print(f"    {agent:15s}: {result['raw_score']:5.1f}% (weight={result['weight']:.1f})")

print(f"\n{'='*90}")
print("COMPARISON:")
print(f"{'='*90}")
print(f"OVER:  {over_analysis.final_confidence}%")
print(f"UNDER: {under_analysis.final_confidence}%")
print(f"Difference: {over_analysis.final_confidence - under_analysis.final_confidence}%")

if under_analysis.final_confidence >= 50:
    print("✅ UNDER is passing 50%+ threshold!")
elif under_analysis.final_confidence >= 45:
    print(f"⚠️  UNDER is close ({under_analysis.final_confidence}% - only {50 - under_analysis.final_confidence}% away)")
else:
    print(f"❌ UNDER is still low ({under_analysis.final_confidence}%)")

# Check if inversion is happening
over_avg = sum(r['raw_score'] for r in over_analysis.agent_breakdown.values()) / len(over_analysis.agent_breakdown)
under_avg = sum(r['raw_score'] for r in under_analysis.agent_breakdown.values()) / len(under_analysis.agent_breakdown)

print(f"\nAverage Agent Score (OVER): {over_avg:.1f}%")
print(f"Average Agent Score (UNDER): {under_avg:.1f}%")

if abs((over_avg + under_avg) - 100) < 5:
    print("✅ Inversion is working! (OVER + UNDER ≈ 100)")
else:
    print(f"❌ Inversion may not be working (OVER + UNDER = {over_avg + under_avg:.1f})")

# Check bet_type preservation
print(f"\nBet Type Check:")
print(f"  OVER prop.bet_type: {over_analysis.prop.bet_type}")
print(f"  UNDER prop.bet_type: {under_analysis.prop.bet_type}")
if over_analysis.prop.bet_type == 'OVER' and under_analysis.prop.bet_type == 'UNDER':
    print("✅ Bet types are being preserved correctly!")
else:
    print("❌ Bet types are NOT being preserved")
