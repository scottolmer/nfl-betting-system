#!/usr/bin/env python
"""Check if Jordan Love is in roster with correct team"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

import pandas as pd

data_dir = project_root / "data"
roster_file = data_dir / "NFL_roster - Sheet1.csv"

df = pd.read_csv(roster_file)

print("Columns in roster:")
print(df.columns.tolist())

print("\nJordan Love in roster:")
jordan = df[df['Player'].str.contains('jordan love', case=False, na=False)]
if len(jordan) > 0:
    for _, row in jordan.iterrows():
        print(f"  Player: {row.get('Player')}")
        print(f"  Team: {row.get('Team')}")
else:
    print("  NOT FOUND")
    
# Check for green bay players
print("\nGreen Bay players (first 5):")
gb = df[df['Team'] == 'GB']
print(gb[['Player', 'Team']].head())
