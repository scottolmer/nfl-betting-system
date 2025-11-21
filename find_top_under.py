#!/usr/bin/env python
"""Find the highest-confidence UNDER bets"""
import sys
from pathlib import Path

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

# Load data
loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=12)

# Run analysis
analyzer = PropAnalyzer()
all_analyses = analyzer.analyze_all_props(context, min_confidence=0)

# Get only UNDER bets and sort by confidence
under_only = [a for a in all_analyses if getattr(a.prop, 'bet_type', 'OVER') == 'UNDER']
under_sorted = sorted(under_only, key=lambda x: x.final_confidence, reverse=True)

print("="*80)
print("TOP 30 HIGHEST-CONFIDENCE UNDER BETS")
print("="*80)
print(f"\n{'#':<3} {'Confidence':<12} {'Player':<20} {'Stat':<15} {'Line':<6}")
print("-" * 80)

for i, prop in enumerate(under_sorted[:30], 1):
    player = prop.prop.player_name[:19]
    stat = prop.prop.stat_type[:14]
    line = prop.prop.line
    conf = prop.final_confidence
    print(f"{i:<3} {conf:<12} {player:<20} {stat:<15} {line:<6.1f}")

# Count how many above 58%
above_58 = sum(1 for p in under_sorted if p.final_confidence >= 58)
print(f"\nTotal UNDER bets above 58%: {above_58}")
print(f"Highest UNDER confidence: {under_sorted[0].final_confidence if under_sorted else 'N/A'}%")

# Compare to OVER
over_only = [a for a in all_analyses if getattr(a.prop, 'bet_type', 'OVER') == 'OVER']
over_sorted = sorted(over_only, key=lambda x: x.final_confidence, reverse=True)

print(f"\nHighest OVER confidence: {over_sorted[0].final_confidence if over_sorted else 'N/A'}%")
print(f"Total OVER bets above 58%: {sum(1 for p in over_sorted if p.final_confidence >= 58)}")

print("\n" + "="*80)
print("CONFIDENCE GAP ANALYSIS")
print("="*80)
print(f"\nTop 10 OVER bets: {[p.final_confidence for p in over_sorted[:10]]}")
print(f"Top 10 UNDER bets: {[p.final_confidence for p in under_sorted[:10]]}")

avg_over = sum(p.final_confidence for p in over_sorted) / len(over_sorted) if over_sorted else 0
avg_under = sum(p.final_confidence for p in under_sorted) / len(under_sorted) if under_sorted else 0

print(f"\nAverage OVER confidence: {avg_over:.1f}%")
print(f"Average UNDER confidence: {avg_under:.1f}%")
print(f"Gap: {avg_over - avg_under:.1f} percentage points")
