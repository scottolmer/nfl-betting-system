#!/usr/bin/env python
"""Test: what if we allowed confidence to drop by 5-10% to get player diversity?"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader

loader = NFLDataLoader(data_dir=str(project_root / "data"))
analyzer = PropAnalyzer()

week = 9
min_conf = 50

print(f"\n📊 Checking if lower confidence props are available for diversity...\n")

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

print(f"Total props: {len(all_analyses)}\n")

# Check how many players are available at different confidence levels
for threshold in [50, 48, 46, 44, 42, 40]:
    above = [a for a in all_analyses if a.final_confidence >= threshold]
    unique_players = len(set(a.prop.player_name for a in above))
    avg_conf = sum(a.final_confidence for a in above) / len(above) if above else 0
    print(f"≥ {threshold}% confidence: {len(above):4d} props from {unique_players:3d} unique players (avg: {avg_conf:.1f}%)")

print("\n💡 Insight: If we relaxed to 48% confidence, could we get more players?")
print("   But that might hurt parlay quality. Trade-off between:")
print("   • High confidence (current: 12 players)")
print("   • Player diversity (potential: more players at lower confidence)")
