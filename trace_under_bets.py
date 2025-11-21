#!/usr/bin/env python
"""Trace where UNDER bets are being filtered out"""
import sys
from pathlib import Path

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.analysis.parlay_optimizer import ParlayOptimizer

print("="*80)
print("TRACING WHERE UNDER BETS ARE LOST")
print("="*80)

# Load data
loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=12)

# Run analysis using analyze_all_props() which creates BOTH OVER and UNDER
analyzer = PropAnalyzer()
all_analyses = analyzer.analyze_all_props(context, min_confidence=0)

# Separate by bet type
over_all = [a for a in all_analyses if getattr(a.prop, 'bet_type', 'OVER') == 'OVER']
under_all = [a for a in all_analyses if getattr(a.prop, 'bet_type', 'OVER') == 'UNDER']

print(f"\n1️⃣  AFTER ANALYSIS:")
print(f"   OVER:  {len(over_all)} ({sum(1 for a in over_all if a.final_confidence >= 58)} above 58%)")
print(f"   UNDER: {len(under_all)} ({sum(1 for a in under_all if a.final_confidence >= 58)} above 58%)")

# Filter to 58+ (what parlay builder uses)
eligible_58 = [a for a in all_analyses if a.final_confidence >= 58]
over_58 = [a for a in eligible_58 if getattr(a.prop, 'bet_type', 'OVER') == 'OVER']
under_58 = [a for a in eligible_58 if getattr(a.prop, 'bet_type', 'OVER') == 'UNDER']

print(f"\n2️⃣  AFTER 58% FILTER (what parlay builder receives):")
print(f"   OVER:  {len(over_58)}")
print(f"   UNDER: {len(under_58)}")

# Try building with traditional builder
print(f"\n3️⃣  TRADITIONAL PARLAY BUILDER:")
builder = ParlayBuilder()
parlays = builder.build_parlays(eligible_58, min_confidence=58)

total_legs = sum(len(p.legs) for p in parlays['2-leg'] + parlays['3-leg'] + parlays['4-leg'] + parlays['5-leg'])
print(f"   Built {sum(len(p) for p in parlays.values())} parlays with {total_legs} total legs")

# Count bet types in parlays
over_count = 0
under_count = 0
for ptype in parlays:
    for parlay in parlays[ptype]:
        for leg in parlay.legs:
            if getattr(leg.prop, 'bet_type', 'OVER') == 'OVER':
                over_count += 1
            else:
                under_count += 1

print(f"   Bet types in parlays:")
print(f"   OVER:  {over_count}")
print(f"   UNDER: {under_count}")

# Try optimizer
print(f"\n4️⃣  PARLAY OPTIMIZER (min_confidence=65):")
optimizer = ParlayOptimizer()
opt_parlays = optimizer.rebuild_parlays_low_correlation(
    eligible_58, 
    target_parlays=10, 
    min_confidence=65,
    max_player_exposure=1.0
)

# Count bet types in opt parlays
over_opt = 0
under_opt = 0
for ptype in opt_parlays:
    for parlay in opt_parlays[ptype]:
        for leg in parlay.legs:
            if getattr(leg.prop, 'bet_type', 'OVER') == 'OVER':
                over_opt += 1
            else:
                under_opt += 1

print(f"   Bet types in optimized parlays:")
print(f"   OVER:  {over_opt}")
print(f"   UNDER: {under_opt}")

print("\n" + "="*80)
print("DIAGNOSIS:")
print("="*80)

if under_58 == 0:
    print("❌ NO UNDER BETS above 58% - increase min_confidence or lower threshold")
elif under_count == 0 and under_opt == 0:
    print("❌ UNDER BETS exist but NOT SELECTED by builders")
    print("   Likely cause: Builder logic prefers OVER or filters by bet_type")
else:
    print("✅ UNDER BETS are being selected!")
