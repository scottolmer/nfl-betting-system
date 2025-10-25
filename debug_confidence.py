#!/usr/bin/env python3
"""Debug why props have 50 confidence"""

import sys
sys.path.insert(0, 'scripts')

from analysis.data_loader import NFLDataLoader
from analysis.orchestrator import PropAnalyzer
from scripts.run_analysis import transform_betting_lines_to_props
from pathlib import Path

data_dir = Path('data')
loader = NFLDataLoader(str(data_dir))
context = loader.load_all_data(week=8)

# Transform props
context['props'] = transform_betting_lines_to_props(context['betting_lines'], 8)
print(f"Created {len(context['props'])} props\n")

# Analyze a few
analyzer = PropAnalyzer()

# Find a WR prop for a player we know has usage data
target_player = 'jaxon smith-njigba'
wr_props = [p for p in context['props'] if p['position'] == 'WR' and target_player in p['player_name'].lower()]

print(f"Found {len(wr_props)} WR props for '{target_player}'")

if wr_props:
    test_prop = wr_props[0]
    print(f"\nAnalyzing: {test_prop}")
    
    analysis = analyzer.analyze_prop(test_prop, context)
    
    print(f"\nResults:")
    print(f"  Final Confidence: {analysis.final_confidence}")
    print(f"  Recommendation: {analysis.recommendation}")
    print(f"\nAgent Breakdown:")
    for agent_name, result in analysis.agent_breakdown.items():
        print(f"  {agent_name}: {result['raw_score']} (rationale: {result['rationale'][:50] if result['rationale'] else 'none'}...)")
else:
    print(f"No props found for {target_player}")
    
    # Show what we got
    print(f"\nSample props:")
    for prop in context['props'][:10]:
        print(f"  {prop['player_name']} ({prop['position']}) - {prop['stat_type']}")
