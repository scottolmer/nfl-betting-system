#!/usr/bin/env python
"""Debug betting lines transformation"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

import pandas as pd

data_dir = project_root / "data"
wk8_file = data_dir / "wk8_betting_lines_draftkings.csv"

df = pd.read_csv(wk8_file)

print("Columns in wk8_betting_lines_draftkings.csv:")
print(df.columns.tolist())

print("\nFirst row:")
print(df.iloc[0])

print("\nJordan Love rows:")
jordan = df[df['description'].str.contains('jordan love', case=False, na=False)]
for _, row in jordan.head(1).iterrows():
    print(f"  description: {row.get('description')}")
    print(f"  home_team: {row.get('home_team')}")
    print(f"  away_team: {row.get('away_team')}")
    print(f"  market: {row.get('market')}")
    print(f"  point: {row.get('point')}")
    print(f"  label: {row.get('label')}")
