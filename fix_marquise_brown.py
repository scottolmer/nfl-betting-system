#!/usr/bin/env python3
"""
Fix Marquise Brown team assignment
Run this to update the roster
"""
import pandas as pd

# Load roster
roster_df = pd.read_csv("data/NFL_roster - Sheet1.csv")

# Find and fix Marquise Brown
def normalize_name(name):
    if not name: return name
    name = str(name).strip().replace('.', '')
    return name.lower()

# Update Marquise Brown
mask = roster_df['Player'].apply(lambda x: 'marquise' in normalize_name(x) and 'brown' in normalize_name(x))
if mask.any():
    print(f"Found {mask.sum()} Marquise Brown entries")
    for idx in roster_df[mask].index:
        old_team = roster_df.loc[idx, 'Team']
        print(f"  Current: {roster_df.loc[idx, 'Player']} - {old_team}")
        roster_df.loc[idx, 'Team'] = 'WAS'
        print(f"  Updated to: WAS")
else:
    print("Marquise Brown not found - adding new entry")
    new_row = pd.DataFrame({
        'Player': ['Marquise Brown'],
        'Position': ['WR'],
        'Team': ['WAS']
    })
    roster_df = pd.concat([roster_df, new_row], ignore_index=True)
    print("  Added: Marquise Brown,WR,WAS")

# Save
roster_df.to_csv("data/NFL_roster - Sheet1.csv", index=False)
print("\n✓ Roster updated!")
print("\nNow re-run:")
print("  python scripts/run_analysis.py --week 8 --skip-fetch")
