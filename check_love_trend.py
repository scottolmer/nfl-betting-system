#!/usr/bin/env python
"""Check Jordan Love trend data"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader

loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=8)

trends = context.get('trends', {})
player_trend = trends.get('jordan love', {})

print("Jordan Love trend data:")
print(player_trend)
