#!/usr/bin/env python3
"""
Trace OVER vs UNDER confidence after fix
Run this in your nfl-betting-systemv2 directory:
    python trace_under_fix.py
"""

import sys
sys.path.insert(0, 'scripts')

from analysis.orchestrator import PropAnalyzer
from analysis.data_loader import load_betting_lines, load_roster, build_context

def main():
    # Load a week's data
    betting_lines = load_betting_lines('data/wk12_betting_lines_draftkings.csv')
    roster = load_roster('data/NFL_roster - Sheet1.csv')
    
    # Build context
    context = build_context(betting_lines, roster, week=12)
    
    # Initialize analyzer
    analyzer = PropAnalyzer()
    
    # Analyze all props
    results = analyzer.analyze_all_props(context, min_confidence=50)
    
    print("=" * 90)
    print("ANALYZING: ALL PROPS (OVER + UNDER)")
    print("=" * 90)
    
    # Separate OVER and UNDER
    overs = [r for r in results if r.prop.bet_type == 'OVER']
    unders = [r for r in results if r.prop.bet_type == 'UNDER']
    
    print(f"\nRESULTS:")
    print(f"  Total OVER bets (>50% conf): {len(overs)}")
    print(f"  Total UNDER bets (>50% conf): {len(unders)}")
    print(f"  Total props: {len(results)}")
    
    if overs:
        over_confs = [r.final_confidence for r in overs]
        print(f"\nOVER Confidence Stats:")
        print(f"  Mean: {sum(over_confs)/len(over_confs):.1f}%")
        print(f"  Median: {sorted(over_confs)[len(over_confs)//2]:.1f}%")
        print(f"  Max: {max(over_confs)}%")
        print(f"  Min: {min(over_confs)}%")
        print(f"  Top 5: {sorted(over_confs, reverse=True)[:5]}")
    
    if unders:
        under_confs = [r.final_confidence for r in unders]
        print(f"\nUNDER Confidence Stats:")
        print(f"  Mean: {sum(under_confs)/len(under_confs):.1f}%")
        print(f"  Median: {sorted(under_confs)[len(under_confs)//2]:.1f}%")
        print(f"  Max: {max(under_confs)}%")
        print(f"  Min: {min(under_confs)}%")
        print(f"  Top 5: {sorted(under_confs, reverse=True)[:5]}")
    
    if overs and unders:
        over_confs = [r.final_confidence for r in overs]
        under_confs = [r.final_confidence for r in unders]
        over_avg = sum(over_confs) / len(over_confs)
        under_avg = sum(under_confs) / len(under_confs)
        print(f"\n{'='*90}")
        print(f"COMPARISON:")
        print(f"  Average OVER:  {over_avg:.1f}%")
        print(f"  Average UNDER: {under_avg:.1f}%")
        print(f"  Gap: {abs(over_avg - under_avg):.1f}%")
        print(f"\n✅ If gap is ~0%, UNDER confidence is now independent!")
        print(f"⚠️  If gap is >3%, there's still a bias.")
        print(f"{'='*90}")
    
    # Show some examples
    print(f"\nTop 10 OVER bets:")
    for i, r in enumerate(sorted(overs, key=lambda x: x.final_confidence, reverse=True)[:10], 1):
        print(f"  {i:2d}. {r.prop.player_name:20s} {r.prop.stat_type:10s} @ {r.prop.line:5.1f} {r.final_confidence}%")
    
    print(f"\nTop 10 UNDER bets:")
    for i, r in enumerate(sorted(unders, key=lambda x: x.final_confidence, reverse=True)[:10], 1):
        print(f"  {i:2d}. {r.prop.player_name:20s} {r.prop.stat_type:10s} @ {r.prop.line:5.1f} {r.final_confidence}%")

if __name__ == '__main__':
    main()
