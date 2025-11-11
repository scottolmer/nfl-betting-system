#!/usr/bin/env python
"""Find Jordan Love in usage data"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
import logging
logging.basicConfig(level=logging.WARNING)

data_dir = project_root / "data"
loader = NFLDataLoader(data_dir=str(data_dir))

context = loader.load_all_data(week=8)

# Search for Jordan Love variations
search_terms = ['jordan love', 'jalen hurts', 'lamar jackson', 'patrick mahomes']

for search in search_terms:
    print(f"\nSearching for: {search}")
    found = False
    for player_name in context.get('usage', {}).keys():
        if search.split()[0].lower() in player_name.lower():
            print(f"  ✓ Found: {player_name}")
            print(f"    {context['usage'][player_name]}")
            found = True
    if not found:
        print(f"  ✗ Not found")

# List all QBs (players with pass attempts)
print("\n" + "="*60)
print("All QBs in usage data:")
print("="*60)
for player_name, usage in context.get('usage', {}).items():
    if usage.get('pass_attempts'):
        print(f"{player_name}: {usage.get('pass_attempts')} pass attempts")
