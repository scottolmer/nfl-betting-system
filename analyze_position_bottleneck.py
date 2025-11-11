#!/usr/bin/env python
"""Analyze why only 12 players are selected - check positions and why others are excluded"""

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

print(f"\n📊 Analyzing position distribution of available players...\n")

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

# Get unique players with their best confidence and position
player_info = {}
for analysis in eligible:
    player = analysis.prop.player_name
    pos = analysis.prop.position
    conf = analysis.final_confidence
    
    if player not in player_info:
        player_info[player] = {'position': pos, 'best_conf': conf, 'count': 0}
    else:
        if conf > player_info[player]['best_conf']:
            player_info[player]['best_conf'] = conf
    player_info[player]['count'] += 1

# Group by position
by_position = {}
for player, info in player_info.items():
    pos = info['position']
    if pos not in by_position:
        by_position[pos] = []
    by_position[pos].append((player, info['best_conf'], info['count']))

print("📊 PLAYERS BY POSITION (at 50%+ confidence):")
print("="*70)
for pos in sorted(by_position.keys()):
    players = sorted(by_position[pos], key=lambda x: x[1], reverse=True)
    print(f"\n{pos}: {len(players)} players")
    for player, conf, count in players[:10]:  # Show top 10 per position
        print(f"  • {player:20s} conf: {conf:5.1f}%  ({count} props)")
    if len(players) > 10:
        print(f"  ... and {len(players)-10} more")

print("\n" + "="*70)
print("KEY INSIGHT:")
print(f"Total players at 50%+ conf: {len(player_info)}")
print(f"By position:")
for pos in sorted(by_position.keys()):
    print(f"  {pos}: {len(by_position[pos])}")
print("\nFor 10 parlays (32 legs), you need diversity across positions.")
print("If you only have a few high-confidence players per position,")
print("the algorithm can't build parlays without reusing them.")
