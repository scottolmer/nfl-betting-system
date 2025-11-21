#!/usr/bin/env python
"""
Debug script - check what props are actually in the data
"""

import sys
from pathlib import Path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader

# Load data
loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=12)

props = context.get('props', [])
print(f"Total props: {len(props)}")

# Count by bet_type
over_count = sum(1 for p in props if p.get('bet_type', '').lower() == 'over')
under_count = sum(1 for p in props if p.get('bet_type', '').lower() == 'under')

print(f"OVER bets: {over_count}")
print(f"UNDER bets: {under_count}")

# Group by player/stat
player_stat_combos = {}
for prop in props:
    key = (prop['player_name'], prop['stat_type'])
    if key not in player_stat_combos:
        player_stat_combos[key] = {'OVER': [], 'UNDER': []}
    
    bet_type = 'UNDER' if prop.get('bet_type', '').lower() == 'under' else 'OVER'
    player_stat_combos[key][bet_type].append(prop)

# Find combos with BOTH OVER and UNDER
both_count = sum(1 for combo, bets in player_stat_combos.items() if bets['OVER'] and bets['UNDER'])
print(f"\nPlayer/stat combos with BOTH OVER and UNDER: {both_count}")

if both_count > 0:
    # Show first example
    for combo, bets in player_stat_combos.items():
        if bets['OVER'] and bets['UNDER']:
            print(f"\nExample: {combo[0]} - {combo[1]}")
            print(f"  OVER bets: {len(bets['OVER'])}")
            for b in bets['OVER'][:2]:
                print(f"    @ {b.get('line')} (bet_type={b.get('bet_type')})")
            print(f"  UNDER bets: {len(bets['UNDER'])}")
            for b in bets['UNDER'][:2]:
                print(f"    @ {b.get('line')} (bet_type={b.get('bet_type')})")
            break
else:
    print("\n⚠️  No player/stat combos with BOTH OVER and UNDER")
    print("\nSample props:")
    for prop in props[:20]:
        print(f"  {prop['player_name']:20s} {prop['stat_type']:15s} @ {prop['line']:5.1f} ({prop.get('bet_type', 'UNKNOWN')})")
