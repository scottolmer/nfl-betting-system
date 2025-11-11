#!/usr/bin/env python
"""Check game_total and spread for Jordan Love"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader

loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=8)

for prop in context.get('props', []):
    if 'jordan love' in prop.get('player_name', '').lower():
        print(f"Jordan Love prop:")
        print(f"  game_total: {prop.get('game_total')}")
        print(f"  spread: {prop.get('spread')}")
        print(f"  is_home: {prop.get('is_home')}")
        break
