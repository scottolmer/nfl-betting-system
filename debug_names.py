#!/usr/bin/env python3
"""Debug name matching between props and aggregated usage data"""

import sys
sys.path.insert(0, 'scripts')

from analysis.data_loader import NFLDataLoader
from pathlib import Path

data_dir = Path('data')
loader = NFLDataLoader(str(data_dir))

context = loader.load_all_data(week=8)

print("\n=== USAGE DATA SAMPLE ===")
usage_names = list(context['usage'].keys())[:10]
for name in usage_names:
    print(f"  '{name}'")

print("\n=== BETTING LINES SAMPLE ===")
if context['betting_lines'] is not None:
    df = context['betting_lines']
    print(f"Columns: {df.columns.tolist()}")
    
    # Show first 10 unique player names
    player_cols = [col for col in df.columns if 'player' in col.lower() or 'name' in col.lower() or 'description' in col.lower()]
    print(f"Player columns: {player_cols}")
    
    if player_cols:
        for col in player_cols:
            print(f"\n  From '{col}':")
            sample = df[col].dropna().unique()[:5]
            for name in sample:
                print(f"    '{name}'")
