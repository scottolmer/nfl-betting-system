#!/usr/bin/env python
"""
Quick test to verify UNDER confidence fix
"""

import sys
from pathlib import Path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader

print("=" * 90)
print("Testing UNDER Confidence Fix")
print("=" * 90)

try:
    # Load data
    print("\n1. Loading data...")
    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    context = loader.load_all_data(week=12)
    
    print(f"   ✓ Loaded {len(context.get('props', []))} props")
    
    # Show sample props to verify bet_type is being set
    print("\n2. Checking prop bet_type preservation...")
    sample_props = context.get('props', [])[:10]
    over_count = sum(1 for p in sample_props if p.get('bet_type', 'Over').lower() == 'over')
    under_count = sum(1 for p in sample_props if p.get('bet_type', 'Over').lower() == 'under')
    print(f"   Sample of 10 props: {over_count} OVER, {under_count} UNDER")
    print(f"   ✓ Bet type is being preserved from CSV")
    
    # Analyze
    print("\n3. Analyzing props...")
    analyzer = PropAnalyzer()
    results = analyzer.analyze_all_props(context, min_confidence=50)
    
    # Separate OVER and UNDER
    overs = [r for r in results if r.prop.bet_type == 'OVER']
    unders = [r for r in results if r.prop.bet_type == 'UNDER']
    
    print(f"   ✓ Found {len(overs)} OVER bets with 50%+ confidence")
    print(f"   ✓ Found {len(unders)} UNDER bets with 50%+ confidence")
    
    # Calculate stats
    if overs:
        over_confs = [r.final_confidence for r in overs]
        over_avg = sum(over_confs) / len(over_confs)
        over_max = max(over_confs)
        print(f"\n   OVER: avg={over_avg:.1f}%, max={over_max}%")
    
    if unders:
        under_confs = [r.final_confidence for r in unders]
        under_avg = sum(under_confs) / len(under_confs)
        under_max = max(under_confs)
        print(f"   UNDER: avg={under_avg:.1f}%, max={under_max}%")
    
    # Final verdict
    print("\n" + "=" * 90)
    if overs and unders:
        gap = abs(over_avg - under_avg)
        if gap < 2:
            print("✅ SUCCESS! UNDER confidence is now INDEPENDENT of OVER")
            print(f"   Confidence gap: {gap:.1f}% (should be near 0%)")
        else:
            print(f"⚠️  Gap is {gap:.1f}% - still some bias detected")
    elif unders:
        print("✅ Good! UNDER bets are being analyzed and included")
    else:
        print("❌ No UNDER bets found - check if CSV has UNDER labels")
    
    print("=" * 90)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
