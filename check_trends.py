#!/usr/bin/env python
"""Check trends data"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader

loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=8)

print(f"Trends dict size: {len(context.get('trends', {}))}")
print(f"Usage dict size: {len(context.get('usage', {}))}")

if context.get('trends'):
    print("\nSample trends:")
    for player, data in list(context['trends'].items())[:3]:
        print(f"  {player}: {data}")
else:
    print("No trends data!")
