#!/usr/bin/env python
"""Trace through data_loader to see why opponent is wrong"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
import logging
logging.basicConfig(level=logging.WARNING)

loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=8)

# Find Jordan Love prop
for prop in context.get('props', []):
    if 'jordan love' in prop.get('player_name', '').lower():
        print(f"Jordan Love prop:")
        print(f"  player_name: {prop.get('player_name')}")
        print(f"  team: {prop.get('team')}")
        print(f"  opponent: {prop.get('opponent')}")
        print(f"  stat_type: {prop.get('stat_type')}")
        print(f"  line: {prop.get('line')}")
        break
