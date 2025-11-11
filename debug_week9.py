#!/usr/bin/env python
"""Debug prop loading and scoring for Week 9"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

loader = NFLDataLoader(data_dir="data")
analyzer = PropAnalyzer()

print("\n📊 Loading Week 9 data...")
context = loader.load_all_data(week=9)

props = context.get('props', [])
print(f"Total props loaded: {len(props)}\n")

if props:
    print("Sample props:")
    for i, p in enumerate(props[:5], 1):
        print(f"{i}. {p.get('player_name')} ({p.get('team')}) vs {p.get('opponent')}")
        print(f"   {p.get('stat_type')} O{p.get('line')}")
    
    print(f"\n\nAnalyzing sample prop...")
    analysis = analyzer.analyze_prop(props[0], context)
    
    print(f"\nPlayer: {analysis.prop.player_name}")
    print(f"Confidence: {analysis.final_confidence}")
    print(f"\nAgent Breakdown:")
    for name, data in sorted(analysis.agent_breakdown.items(), 
                            key=lambda x: x[1]['raw_score'], reverse=True):
        print(f"  {name}: {data['raw_score']} (weight: {data['weight']})")
        if data.get('rationale'):
            for r in data['rationale'][:2]:
                print(f"    - {r}")
else:
    print("❌ No props loaded!")
    print("\nChecking data files...")
    print(f"DVOA Off: {len(context.get('dvoa_offensive', {}))} teams")
    print(f"DVOA Def: {len(context.get('dvoa_defensive', {}))} teams")
    print(f"Usage: {len(context.get('usage', {}))} players")
