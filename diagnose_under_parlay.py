#!/usr/bin/env python3
"""Quick diagnostic to see what's actually being passed to parlay builder"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader

# Setup
analyzer = PropAnalyzer()
loader = NFLDataLoader(data_dir=str(Path.cwd() / "data"))

# Load data
context = loader.load_all_data(week=9)

print("\n" + "="*80)
print("DIAGNOSTIC: What gets passed to parlay builder?")
print("="*80 + "\n")

# Analyze all props
print("Step 1: Running analyze_all_props()...")
all_analyses = analyzer.analyze_all_props(context, min_confidence=40)

print(f"\n✅ Got {len(all_analyses)} analyses total\n")

# Breakdown by bet_type
over_analyses = [a for a in all_analyses if getattr(a.prop, 'bet_type', 'OVER') == 'OVER']
under_analyses = [a for a in all_analyses if getattr(a.prop, 'bet_type', 'OVER') == 'UNDER']

print(f"   OVER bets: {len(over_analyses)}")
print(f"   UNDER bets: {len(under_analyses)}")

# Show all UNDER bets
if under_analyses:
    print(f"\n📊 ALL UNDER BETS IN all_analyses:")
    print("="*80)
    for i, analysis in enumerate(under_analyses, 1):
        prop = analysis.prop
        print(f"{i}. {prop.player_name:20s} ({prop.team:3s}) {prop.stat_type:15s} U{prop.line:6.1f} | Conf: {analysis.final_confidence:5.1f}%")
else:
    print("\n❌ NO UNDER BETS FOUND in all_analyses!")

# Now simulate what the parlay builder does
print(f"\n" + "="*80)
print("Step 2: Simulating parlay builder filtering...")
print("="*80 + "\n")

min_conf = 58
eligible_props = sorted(
    [prop for prop in all_analyses if prop.final_confidence >= min_conf],
    key=lambda x: x.final_confidence,
    reverse=True
)

print(f"After filtering to {min_conf}+ confidence:")
print(f"   Total eligible: {len(eligible_props)}")

over_eligible = [p for p in eligible_props if getattr(p.prop, 'bet_type', 'OVER') == 'OVER']
under_eligible = [p for p in eligible_props if getattr(p.prop, 'bet_type', 'OVER') == 'UNDER']

print(f"   OVER eligible: {len(over_eligible)}")
print(f"   UNDER eligible: {len(under_eligible)}")

if under_eligible:
    print(f"\n📊 UNDER BETS THAT PASSED {min_conf}+ FILTER:")
    print("="*80)
    for i, analysis in enumerate(under_eligible, 1):
        prop = analysis.prop
        print(f"{i}. {prop.player_name:20s} ({prop.team:3s}) {prop.stat_type:15s} U{prop.line:6.1f} | Conf: {analysis.final_confidence:5.1f}%")
else:
    print(f"\n❌ NO UNDER BETS PASSED {min_conf}+ CONFIDENCE FILTER!")
    print("\n   This means all UNDERs are below 58% confidence")
    print("   (which is expected if they're inversions of low-confidence OVERs)")

print("\n" + "="*80 + "\n")
