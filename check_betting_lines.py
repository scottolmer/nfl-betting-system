#!/usr/bin/env python
"""Check what betting lines file is being loaded"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

import pandas as pd

data_dir = project_root / "data"

# Check what files exist
print("Week 8 Betting Lines Files:")
for f in data_dir.glob("wk8_betting_lines*"):
    print(f"  ✓ {f.name}")

print("\nWeek 7 Betting Lines Files:")
for f in data_dir.glob("wk7_betting_lines*"):
    print(f"  ✓ {f.name}")

# Load wk8 and check matchups
wk8_file = data_dir / "wk8_betting_lines_draftkings.csv"
if wk8_file.exists():
    df = pd.read_csv(wk8_file)
    print(f"\n✓ Loaded {wk8_file.name}")
    
    # Find Jordan Love props
    jordan_props = df[df['description'].str.contains('jordan love', case=False, na=False)]
    
    if len(jordan_props) > 0:
        print(f"\nJordan Love props in wk8_betting_lines_draftkings.csv:")
        for _, row in jordan_props.head(3).iterrows():
            print(f"  {row.get('description')}: {row.get('home_team')} vs {row.get('away_team')}")
    else:
        print("No Jordan Love props found")
        
    # Show teams in the file
    print(f"\nTeams in file:")
    home_teams = df['home_team'].unique()
    away_teams = df['away_team'].unique()
    for h, a in zip(sorted(home_teams)[:5], sorted(away_teams)[:5]):
        print(f"  {h} vs {a}")
