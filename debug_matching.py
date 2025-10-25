#!/usr/bin/env python3
"""Debug prop name matching"""

import sys
sys.path.insert(0, 'scripts')

from analysis.data_loader import NFLDataLoader
from analysis.agents.volume_agent import VolumeAgent, normalize_player_name
from pathlib import Path
import re

data_dir = Path('data')
loader = NFLDataLoader(str(data_dir))
context = loader.load_all_data(week=8)

# Get some player names from usage
usage_names = list(context['usage'].keys())[:5]
print("=== USAGE DATA NAMES ===")
for name in usage_names:
    print(f"  '{name}'")

# Get some prop names
print("\n=== PROP NAMES (from betting lines) ===")
if context['betting_lines'] is not None:
    df = context['betting_lines']
    prop_names = df['player_name'].dropna().unique()[:10]
    for name in prop_names:
        print(f"  '{name}'")

# Test the transform function
print("\n=== TESTING TRANSFORM ===")
from scripts.run_analysis import transform_betting_lines_to_props

props = transform_betting_lines_to_props(context['betting_lines'], 8)
print(f"Transformed {len(props)} props")

# Show sample transformed names
print("\nSample transformed prop names:")
for prop in props[:5]:
    print(f"  '{prop['player_name']}'")

# Test matching
print("\n=== TESTING VOLUME AGENT ===")
agent = VolumeAgent()

# Create fake prop object
class FakeProp:
    def __init__(self, name, pos):
        self.player_name = name
        self.position = pos

# Try matching a known player
test_name = "jaxon smith-njigba"
test_prop = FakeProp(test_name, 'WR')

score, direction, rationale = agent.analyze(test_prop, context)
print(f"\nTesting '{test_name}':")
print(f"  Score: {score}")
print(f"  Direction: {direction}")
print(f"  Rationale: {rationale}")

# Check if name is in usage
print(f"\n  In usage data? {test_name in context['usage']}")
print(f"  Usage data keys sample: {list(context['usage'].keys())[:5]}")
