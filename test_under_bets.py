#!/usr/bin/env python
"""Test if UNDER bets are being loaded"""
import sys
from pathlib import Path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader

print("Testing UNDER bets loading...\n")

loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=12)

props = context.get('props', [])
print(f"Total props loaded: {len(props)}")

# Check bet_type distribution
bet_types = {}
for prop in props:
    bt = prop.get('bet_type', 'MISSING')
    bet_types[bt] = bet_types.get(bt, 0) + 1

print(f"\nBet type distribution in props:")
for bt, count in sorted(bet_types.items()):
    print(f"  {bt}: {count}")

# Show first 10 props
print(f"\nFirst 10 props:")
for i, prop in enumerate(props[:10], 1):
    print(f"{i:2d}. {prop.get('player_name'):20s} {prop.get('stat_type'):20s} {prop.get('bet_type'):5s} @ {prop.get('line'):6.1f}")

# Check raw betting lines
print(f"\n" + "="*80)
print("Checking raw betting lines...")
betting_lines_raw = context.get('betting_lines_raw')
if betting_lines_raw is not None:
    print(f"Raw betting lines shape: {betting_lines_raw.shape}")
    print(f"Columns: {list(betting_lines_raw.columns)}")
    
    if 'label' in betting_lines_raw.columns:
        label_counts = betting_lines_raw['label'].value_counts()
        print(f"\nLabel distribution in RAW data:")
        for label, count in label_counts.items():
            print(f"  {label}: {count}")
    else:
        print("⚠️  'label' column not found in raw betting lines!")
else:
    print("❌ No raw betting lines loaded!")
