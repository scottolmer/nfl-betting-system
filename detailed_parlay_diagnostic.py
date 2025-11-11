#!/usr/bin/env python
"""Detailed diagnostic of parlay building to see where it's bottlenecking"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.parlay_builder import ParlayBuilder

loader = NFLDataLoader(data_dir=str(project_root / "data"))
analyzer = PropAnalyzer()

week = 9
min_conf = 50

print(f"\n📊 Detailed parlay building diagnostic...\n")

# Load and analyze
context = loader.load_all_data(week=week)
props_list = context.get('props', [])

all_analyses = []
for i, prop in enumerate(props_list, 1):
    try:
        analysis = analyzer.analyze_prop(prop, context)
        if analysis:
            all_analyses.append(analysis)
    except Exception as e:
        pass

eligible = [p for p in all_analyses if p.final_confidence >= min_conf]
print(f"✅ {len(eligible)} props at {min_conf}%+ confidence\n")

# Build parlays with detailed output
print("Building parlays (showing each parlay type):\n")
builder = ParlayBuilder()
parlays = builder.build_parlays(all_analyses, min_confidence=min_conf)

# Count results
print("\n" + "="*70)
print("RESULTS:")
print("="*70)
for leg_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
    count = len(parlays[leg_type])
    if count > 0:
        total_legs = sum(len(p.legs) for p in parlays[leg_type])
        print(f"{leg_type}: {count} parlays ({total_legs} total legs)")
        for idx, parlay in enumerate(parlays[leg_type], 1):
            players = [leg.prop.player_name for leg in parlay.legs]
            print(f"  {leg_type} #{idx}: {', '.join(players)}")
