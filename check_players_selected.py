#!/usr/bin/env python
"""Debug which players the parlay builder actually selects"""

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

print(f"\n📊 Checking which players are selected for parlays...\n")

# Load data
context = loader.load_all_data(week=week)
props_list = context.get('props', [])

# Analyze all props
all_analyses = []
for i, prop in enumerate(props_list, 1):
    try:
        analysis = analyzer.analyze_prop(prop, context)
        if analysis:
            all_analyses.append(analysis)
    except Exception as e:
        pass

print(f"✅ Analyzed {len(all_analyses)} props")

# Filter by confidence
eligible = [p for p in all_analyses if p.final_confidence >= min_conf]
print(f"✅ {len(eligible)} props at {min_conf}%+ confidence")

# Get unique players in eligible pool
eligible_players = set(a.prop.player_name for a in eligible)
print(f"✅ {len(eligible_players)} unique players available\n")

# Build parlays
print("Building parlays...\n")
builder = ParlayBuilder()
parlays = builder.build_parlays(all_analyses, min_confidence=min_conf)

# Extract players used in parlays
used_players = set()
for parlay_type, parlay_list in parlays.items():
    for parlay in parlay_list:
        for leg in parlay.legs:
            used_players.add(leg.prop.player_name)

print(f"\n📊 PLAYERS USED IN PARLAYS:")
print("="*60)
print(f"Unique players used: {len(used_players)}")
print(f"Unique players available: {len(eligible_players)}")
print(f"Unused players: {len(eligible_players) - len(used_players)}\n")

print("Players used:")
for player in sorted(used_players):
    print(f"  • {player}")

print(f"\n✅ Analysis complete")
