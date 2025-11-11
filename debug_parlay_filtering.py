#!/usr/bin/env python
"""Debug parlay builder filtering logic"""

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

print(f"\n📊 Building parlays from Week {week} with min confidence {min_conf}%...\n")

# Load data
context = loader.load_all_data(week=week)
props_list = context.get('props', [])

# Analyze all props
all_analyses = []
for i, prop in enumerate(props_list, 1):
    if i % 200 == 0:
        print(f"Analyzing: {i}/{len(props_list)}")
    try:
        analysis = analyzer.analyze_prop(prop, context)
        if analysis:
            all_analyses.append(analysis)
    except Exception as e:
        pass

print(f"\n✅ Analyzed {len(all_analyses)} props total")

# Filter by confidence
eligible = [p for p in all_analyses if p.final_confidence >= min_conf]
print(f"✅ {len(eligible)} props at {min_conf}%+ confidence")

# Group by position
by_position = {}
for analysis in eligible:
    pos = analysis.prop.position
    if pos not in by_position:
        by_position[pos] = []
    by_position[pos].append(analysis)

print(f"\n📊 PROPS BY POSITION (at {min_conf}%+):")
print("="*60)
for pos in sorted(by_position.keys()):
    count = len(by_position[pos])
    avg_conf = sum(p.final_confidence for p in by_position[pos]) / count
    print(f"{pos:4s}: {count:3d} props (avg conf: {avg_conf:.1f}%)")

print("="*60)

# Now build parlays
builder = ParlayBuilder()
parlays = builder.build_parlays(all_analyses, min_confidence=min_conf)

# Count total legs used
total_legs = 0
for parlay_type, parlay_list in parlays.items():
    for parlay in parlay_list:
        total_legs += len(parlay.legs)

print(f"\n📊 PARLAY RESULTS:")
print(f"2-leg parlays: {len(parlays['2-leg'])}")
print(f"3-leg parlays: {len(parlays['3-leg'])}")
print(f"4-leg parlays: {len(parlays['4-leg'])}")
print(f"5-leg parlays: {len(parlays['5-leg'])}")
print(f"Total legs used: {total_legs}")
print(f"Unique props available: {len(eligible)}")
print(f"Props used: {total_legs}")
print(f"Props unused: {len(eligible) - total_legs}")
