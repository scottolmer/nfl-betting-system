#!/usr/bin/env python
"""Diagnostic script to compare OVER vs UNDER confidence distributions"""
import sys
from pathlib import Path

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

print("Running diagnostic analysis...")
print("="*80)

# Load data
loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=12)

# Run analysis using analyze_all_props() which creates BOTH OVER and UNDER
analyzer = PropAnalyzer()
analyses = analyzer.analyze_all_props(context, min_confidence=0)  # Get all, no filtering

print(f"\nTotal analyses completed: {len(analyses)}")

# Separate by bet type
over_props = [a for a in analyses if getattr(a.prop, 'bet_type', 'OVER') == 'OVER']
under_props = [a for a in analyses if getattr(a.prop, 'bet_type', 'OVER') == 'UNDER']

print(f"\nTotal OVER props:  {len(over_props)}")
print(f"Total UNDER props: {len(under_props)}")

# Calculate stats
if over_props:
    over_confs = [a.final_confidence for a in over_props]
    print(f"\nOVER Confidence Stats:")
    print(f"  Mean:      {sum(over_confs)/len(over_confs):.1f}%")
    print(f"  Median:    {sorted(over_confs)[len(over_confs)//2]:.1f}%")
    print(f"  Min/Max:   {min(over_confs):.1f}% - {max(over_confs):.1f}%")
    print(f"  >= 58%:    {sum(1 for c in over_confs if c >= 58)} ({100*sum(1 for c in over_confs if c >= 58)/len(over_confs):.1f}%)")

if under_props:
    under_confs = [a.final_confidence for a in under_props]
    print(f"\nUNDER Confidence Stats:")
    print(f"  Mean:      {sum(under_confs)/len(under_confs):.1f}%")
    print(f"  Median:    {sorted(under_confs)[len(under_confs)//2]:.1f}%")
    print(f"  Min/Max:   {min(under_confs):.1f}% - {max(under_confs):.1f}%")
    print(f"  >= 58%:    {sum(1 for c in under_confs if c >= 58)} ({100*sum(1 for c in under_confs if c >= 58)/len(under_confs):.1f}%)")

# Compare the difference
if over_props and under_props:
    over_avg = sum(over_confs) / len(over_confs)
    under_avg = sum(under_confs) / len(under_confs)
    diff = over_avg - under_avg
    print(f"\n{'='*80}")
    print(f"KEY FINDING: OVER avg {over_avg:.1f}% vs UNDER avg {under_avg:.1f}%")
    print(f"Difference: {diff:+.1f} percentage points")
    if abs(diff) > 3:
        print(f"⚠️  BIAS DETECTED: UNDER bets are systematically {abs(diff):.1f}% lower!")
    else:
        print(f"✅ Confidence scores are balanced between OVER and UNDER")
    print(f"{'='*80}")

# Show sample pairs
print(f"\nSample Props: Comparing OVER vs UNDER Agent Scores")
print("="*80)

over_dict = {(a.prop.player_name, a.prop.stat_type): a for a in over_props}
under_dict = {(a.prop.player_name, a.prop.stat_type): a for a in under_props}

paired_keys = list(set(over_dict.keys()) & set(under_dict.keys()))[:10]

for i, key in enumerate(paired_keys, 1):
    over_analysis = over_dict[key]
    under_analysis = under_dict[key]
    
    player_name = key[0]
    stat_type = key[1]
    
    print(f"\n{i}. {player_name} - {stat_type}")
    
    try:
        over_final = over_analysis.final_confidence
        under_final = under_analysis.final_confidence
        print(f"   OVER:  {over_final:.1f}%")
        print(f"   UNDER: {under_final:.1f}%")
        print(f"   Δ: {under_final - over_final:+.1f}%")
    except Exception as e:
        print(f"   Error accessing scores: {e}")

print("\n" + "="*80)
print("Diagnostic complete!")
