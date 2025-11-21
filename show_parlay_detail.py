#!/usr/bin/env python
"""Show detailed breakdown of what legs are selected in parlays"""
import sys
from pathlib import Path

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder

print("="*80)
print("DETAILED PARLAY LEG ANALYSIS")
print("="*80)

# Load data
loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=12)

# Run analysis
analyzer = PropAnalyzer()
all_analyses = analyzer.analyze_all_props(context, min_confidence=0)

# Filter to 58+
eligible_58 = [a for a in all_analyses if a.final_confidence >= 58]

# Sort by confidence to see what's available
eligible_sorted = sorted(eligible_58, key=lambda x: x.final_confidence, reverse=True)

print(f"\nTop 30 props by confidence (all types):\n")
print(f"{'#':<3} {'Confidence':<12} {'Player':<20} {'Stat':<15} {'Type':<6} {'Line':<6}")
print("-" * 80)

for i, prop in enumerate(eligible_sorted[:30], 1):
    bet_type = getattr(prop.prop, 'bet_type', 'OVER')
    player = prop.prop.player_name[:19]
    stat = prop.prop.stat_type[:14]
    line = prop.prop.line
    conf = prop.final_confidence
    print(f"{i:<3} {conf:<12} {player:<20} {stat:<15} {bet_type:<6} {line:<6.1f}")

# Now build parlays and show what was selected
print("\n" + "="*80)
print("PARLAYS BUILT")
print("="*80)

builder = ParlayBuilder()
parlays = builder.build_parlays(eligible_58, min_confidence=58)

for leg_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
    parlay_list = parlays[leg_type]
    if not parlay_list:
        continue
    
    print(f"\n{leg_type.upper()} PARLAYS ({len(parlay_list)} total):\n")
    
    for p_idx, parlay in enumerate(parlay_list, 1):
        print(f"  Parlay {p_idx} (Confidence: {parlay.combined_confidence}%)")
        for leg_idx, leg in enumerate(parlay.legs, 1):
            bet_type = getattr(leg.prop, 'bet_type', 'OVER')
            print(f"    Leg {leg_idx}: {leg.prop.player_name:<20} {leg.prop.stat_type:<15} {bet_type} {leg.prop.line:<6.1f} @ {leg.final_confidence}%")
        print()

# Now analyze: which high-confidence props were NOT selected?
print("="*80)
print("HIGH-CONFIDENCE PROPS NOT SELECTED")
print("="*80)

selected_prop_ids = set()
for leg_type in parlays:
    for parlay in parlays[leg_type]:
        for leg in parlay.legs:
            prop_id = (leg.prop.player_name, leg.prop.stat_type, leg.prop.line, getattr(leg.prop, 'bet_type', 'OVER'))
            selected_prop_ids.add(prop_id)

print(f"\nTop 20 props that were NOT selected:\n")
print(f"{'#':<3} {'Confidence':<12} {'Player':<20} {'Stat':<15} {'Type':<6} {'Line':<6}")
print("-" * 80)

unselected_count = 0
for prop in eligible_sorted:
    prop_id = (prop.prop.player_name, prop.prop.stat_type, prop.prop.line, getattr(prop.prop, 'bet_type', 'OVER'))
    if prop_id not in selected_prop_ids:
        unselected_count += 1
        if unselected_count <= 20:
            bet_type = getattr(prop.prop, 'bet_type', 'OVER')
            player = prop.prop.player_name[:19]
            stat = prop.prop.stat_type[:14]
            line = prop.prop.line
            conf = prop.final_confidence
            print(f"{unselected_count:<3} {conf:<12} {player:<20} {stat:<15} {bet_type:<6} {line:<6.1f}")

print(f"\nTotal unselected: {unselected_count}")
