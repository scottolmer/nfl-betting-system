#!/usr/bin/env python3
"""
Test the stats aggregation to ensure agents get proper data
"""

import sys
sys.path.insert(0, 'scripts')

from analysis.data_loader import NFLDataLoader
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)

data_dir = Path('data')
loader = NFLDataLoader(str(data_dir))

print("\n" + "="*70)
print("TESTING STATS AGGREGATION")
print("="*70 + "\n")

# Load Week 8 data
context = loader.load_all_data(week=8)

# Check results
print("\n✓ Data Loading Complete\n")

if context.get('usage'):
    print(f"✅ context['usage'] loaded: {len(context['usage'])} players")
    
    # Show sample
    sample_players = list(context['usage'].keys())[:5]
    for player in sample_players:
        stats = context['usage'][player]
        print(f"\n  {player.upper()}:")
        for key, val in stats.items():
            if isinstance(val, float):
                print(f"    {key}: {val:.1f}")
            else:
                print(f"    {key}: {val}")
else:
    print("❌ context['usage'] NOT populated")

if context.get('trends'):
    print(f"\n✅ context['trends'] loaded: {len(context['trends'])} players")
else:
    print("\n❌ context['trends'] NOT populated")

# Check betting lines
if context.get('betting_lines') is not None:
    print(f"\n✅ Betting lines loaded: {len(context['betting_lines'])} props")
else:
    print("\n❌ Betting lines NOT loaded")

print("\n" + "="*70)
print("END OF TEST")
print("="*70 + "\n")
