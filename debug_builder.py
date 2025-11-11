#!/usr/bin/env python
"""Debug: Check if recently_used_players is actually working"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.parlay_builder import ParlayBuilder
from collections import defaultdict

loader = NFLDataLoader(data_dir=str(project_root / "data"))
analyzer = PropAnalyzer()

week = 9
min_conf = 50

print(f"\n📊 Debugging parlay builder...\n")

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
print(f"✅ {len(eligible)} props eligible\n")

# Manually trace through what build_n_leg_parlays would do
used_prop_ids = set()
player_usage_count = defaultdict(int)
recently_used_players = set()

def get_prop_analysis_id(analysis):
    prop = analysis.prop
    return (prop.player_name, prop.stat_type, prop.line, prop.team, prop.opponent)

print("Building 2-leg parlays manually to trace logic:\n")

for parlay_num in range(3):
    print(f"Building 2-leg parlay #{parlay_num + 1}:")
    
    # Sort props
    def prop_sort_key(prop):
        player_name = prop.prop.player_name
        recently_used = 1 if player_name in recently_used_players else 0
        confidence = -prop.final_confidence
        return (recently_used, confidence)
    
    sorted_props = sorted(eligible, key=prop_sort_key)
    
    current_legs = []
    players_in_current = set()
    
    for idx, prop_analysis in enumerate(sorted_props):
        if len(current_legs) >= 2:
            break
        
        prop_id = get_prop_analysis_id(prop_analysis)
        player_name = prop_analysis.prop.player_name
        
        if (prop_id not in used_prop_ids and 
            player_usage_count[player_name] < 3 and 
            player_name not in players_in_current):
            
            current_legs.append((player_name, prop_analysis.final_confidence))
            players_in_current.add(player_name)
            
            if idx < 5 or len(current_legs) == 1:
                print(f"  Leg {len(current_legs)}: {player_name} ({prop_analysis.final_confidence:.1f}%)")
    
    if len(current_legs) == 2:
        for leg in current_legs:
            player = leg[0]
            recently_used_players.add(player)
            player_usage_count[player] += 1
        print(f"  ✅ Built with {', '.join(l[0] for l in current_legs)}")
        print(f"  Recently used now: {recently_used_players}")
    
    print()

print(f"\nFinal player usage:")
for player, count in sorted(player_usage_count.items()):
    print(f"  {player}: {count} uses")
