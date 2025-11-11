#!/usr/bin/env python3
"""
Final diagnostic: Identify missing players and opponent assignment failures
This will tell us EXACTLY what's wrong with week 9
"""
import pandas as pd
from pathlib import Path
import sys
import re

# Normalize functions (copied from data_loader)
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
bet_file = data_dir / "wk9_betting_lines_draftkings.csv"
roster_file = data_dir / "NFL_roster - Sheet1.csv"

print("\n" + "="*120)
print("WEEK 9 OPPONENT ASSIGNMENT - FINAL DIAGNOSTIC")
print("="*120)

if not bet_file.exists():
    print(f"❌ ERROR: Betting lines file not found: {bet_file}")
    sys.exit(1)

if not roster_file.exists():
    print(f"❌ ERROR: Roster file not found: {roster_file}")
    sys.exit(1)

# Load data
print("\n[1] Loading data files...")
df_bet = pd.read_csv(bet_file)
df_roster = pd.read_csv(roster_file)
print(f"  ✓ Betting lines: {len(df_bet)} rows")
print(f"  ✓ Roster: {len(df_roster)} rows")

# Build roster map
print("\n[2] Building roster map...")
player_to_team_map = {}
for _, row in df_roster.iterrows():
    player_name_raw = row.get('Player')
    team_abbr = row.get('Team')
    if player_name_raw and team_abbr:
        normalized_player = normalize_name(player_name_raw)
        normalized_team = normalize_team_abbr(team_abbr)
        player_to_team_map[normalized_player] = normalized_team

print(f"  ✓ Built map with {len(player_to_team_map)} players")

# Get games
print("\n[3] Games in betting lines:")
games = df_bet.drop_duplicates(subset=['home_team', 'away_team'])[['home_team', 'away_team']]
print(f"  Total games: {len(games)}")
for _, row in games.iterrows():
    print(f"    - {row['away_team']} @ {row['home_team']}")

# Get unique players from betting lines
print("\n[4] Unique players in betting lines:")
df_players = df_bet[df_bet['market'].str.contains('player_', case=False, na=False)]
unique_players = sorted(df_players['description'].unique())
print(f"  Total unique players: {len(unique_players)}")
print(f"\n  Checking which players are in roster:")

missing_players = []
found_players = []

for player_raw in unique_players:
    player_norm = normalize_name(player_raw)
    in_roster = player_norm in player_to_team_map
    team = player_to_team_map.get(player_norm, 'N/A')
    
    if in_roster:
        found_players.append((player_raw, team))
        status = f"✓ {team}"
    else:
        missing_players.append(player_raw)
        status = "✗ MISSING"
    
    print(f"    {player_raw:30} -> {status}")

# Summary
print("\n" + "="*120)
print("SUMMARY")
print("="*120)
print(f"\nPlayers found in roster: {len(found_players)}/{len(unique_players)}")
print(f"Players MISSING from roster: {len(missing_players)}/{len(unique_players)}")

if missing_players:
    print(f"\n⚠️  MISSING PLAYERS (causing props to be skipped):")
    for player in missing_players:
        print(f"     - {player}")
    
    print(f"\n❌ FIX: Add these {len(missing_players)} players to NFL_roster - Sheet1.csv with correct team abbreviations")
    print(f"   Format: Player,Position,Team")
    print(f"   Example: De'Von Achane,RB,MIA")

else:
    print(f"\n✓ All players are in the roster!")

# Simulate transformation to see how many props would be created
print(f"\n[5] Simulating transformation...")

TEAM_FULL_NAME_TO_ABBR = {
    'Arizona Cardinals': 'ARI', 'Atlanta Falcons': 'ATL', 'Baltimore Ravens': 'BAL',
    'Buffalo Bills': 'BUF', 'Carolina Panthers': 'CAR', 'Chicago Bears': 'CHI',
    'Cincinnati Bengals': 'CIN', 'Cleveland Browns': 'CLE', 'Dallas Cowboys': 'DAL',
    'Denver Broncos': 'DEN', 'Detroit Lions': 'DET', 'Green Bay Packers': 'GB',
    'Houston Texans': 'HOU', 'Indianapolis Colts': 'IND', 'Jacksonville Jaguars': 'JAC',
    'Kansas City Chiefs': 'KC', 'Las Vegas Raiders': 'LV', 'Los Angeles Chargers': 'LAC',
    'Los Angeles Rams': 'LAR', 'Miami Dolphins': 'MIA', 'Minnesota Vikings': 'MIN',
    'New England Patriots': 'NE', 'New Orleans Saints': 'NO', 'New York Giants': 'NYG',
    'New York Jets': 'NYJ', 'Philadelphia Eagles': 'PHI', 'Pittsburgh Steelers': 'PIT',
    'San Francisco 49ers': 'SF', 'Seattle Seahawks': 'SEA', 'Tampa Bay Buccaneers': 'TB',
    'Tennessee Titans': 'TEN', 'Washington Commanders': 'WAS',
}

def get_abbr(team_name):
    if not team_name or pd.isna(team_name): return ''
    team_name_str = str(team_name).strip()
    if len(team_name_str) <= 3 and team_name_str.isupper():
        return normalize_team_abbr(team_name_str)
    abbr = TEAM_FULL_NAME_TO_ABBR.get(team_name_str)
    if abbr: return normalize_team_abbr(abbr)
    return normalize_team_abbr(team_name_str)

# Count how many props would be created
total_rows = 0
successful_props = 0
skipped_not_in_roster = 0
skipped_team_mismatch = 0

for _, row in df_players.iterrows():
    total_rows += 1
    
    player_name_raw = row.get('description', '')
    player_name_norm = normalize_name(player_name_raw)
    home_team_abbr = get_abbr(row.get('home_team'))
    away_team_abbr = get_abbr(row.get('away_team'))
    
    if not home_team_abbr or not away_team_abbr:
        continue
    
    # Check roster
    player_team_abbr = player_to_team_map.get(player_name_norm)
    
    if not player_team_abbr:
        skipped_not_in_roster += 1
        continue
    
    if player_team_abbr == home_team_abbr:
        opponent_abbr = away_team_abbr
        successful_props += 1
    elif player_team_abbr == away_team_abbr:
        opponent_abbr = home_team_abbr
        successful_props += 1
    else:
        skipped_team_mismatch += 1

print(f"  Player prop rows in betting lines: {total_rows}")
print(f"  ✓ Successfully assigned: {successful_props}")
print(f"  ✗ Skipped (player not in roster): {skipped_not_in_roster}")
print(f"  ✗ Skipped (team mismatch): {skipped_team_mismatch}")

if successful_props < 50:
    print(f"\n❌ WARNING: Only {successful_props} props would be created!")
    print(f"   This is too few. Check roster for missing players.")
else:
    print(f"\n✓ {successful_props} props would be created - looks good!")

print("\n" + "="*120 + "\n")
