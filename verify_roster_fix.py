#!/usr/bin/env python3
"""
Verify that all 6 missing players have been added
"""
import pandas as pd
from pathlib import Path
import re

def normalize_name(name):
    if not name: return name
    name = str(name).strip().replace('.', '')
    name = re.sub(r'\s+', ' ', name)
    return name.lower()

def normalize_team_abbr(abbr):
    if not abbr: return abbr
    abbr = str(abbr).strip().upper()
    team_map = {'JAX': 'JAC', 'ARZ': 'ARI', 'BLT': 'BAL', 'CLV': 'CLE', 'HST': 'HOU'}
    return team_map.get(abbr, abbr)

# Load files
data_dir = Path("data")
roster_file = data_dir / "NFL_roster - Sheet1.csv"

# Load data
df_roster = pd.read_csv(roster_file)

# Build roster map
player_to_team_map = {}
for _, row in df_roster.iterrows():
    player_name_raw = row.get('Player')
    team_abbr = row.get('Team')
    if player_name_raw and team_abbr:
        normalized_player = normalize_name(player_name_raw)
        normalized_team = normalize_team_abbr(team_abbr)
        player_to_team_map[normalized_player] = normalized_team

print("\n" + "="*80)
print("VERIFYING 6 PREVIOUSLY MISSING PLAYERS")
print("="*80)

missing_players_list = [
    "Aaron Jones",
    "Cedrick Wilson Jr.",
    "Greg Dulcich",
    "Kyle Pitts",
    "Oronde Gadsden II",
    "Tre Harris"
]

all_found = True
for player in missing_players_list:
    player_norm = normalize_name(player)
    if player_norm in player_to_team_map:
        team = player_to_team_map[player_norm]
        print(f"✓ {player:30} -> {team}")
    else:
        print(f"✗ {player:30} -> NOT FOUND")
        all_found = False

print("\n" + "="*80)
if all_found:
    print("SUCCESS! All 6 previously missing players have been added to roster!")
    print("\nNow run: python run.py analyze week 9")
else:
    print("ERROR: Some players still missing!")
print("="*80 + "\n")
