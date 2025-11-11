#!/usr/bin/env python
"""Diagnose why agents are scoring 50"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
import logging
logging.basicConfig(level=logging.DEBUG)

data_dir = project_root / "data"
loader = NFLDataLoader(data_dir=str(data_dir))

print("\n" + "="*60)
print("DIAGNOSTIC: Why Are Agents Scoring 50?")
print("="*60)

week = 8
context = loader.load_all_data(week=week)

print(f"\n✓ Usage data loaded: {len(context.get('usage', {}))} players")
print(f"✓ Trends data loaded: {len(context.get('trends', {}))} players")
print(f"✓ Props loaded: {len(context.get('props', []))}")

# Check first player
if context.get('usage'):
    first_player = list(context['usage'].keys())[0]
    print(f"\n📋 Sample usage data for: {first_player}")
    print(f"   {context['usage'][first_player]}")
else:
    print("\n❌ NO USAGE DATA FOUND - This is why agents score 50!")
    print("\nFiles needed for Week 8:")
    for f in ['wk8_receiving_base.csv', 'wk8_receiving_usage.csv', 
              'wk8_rushing_base.csv', 'wk8_rushing_usage.csv',
              'wk8_passing_base.csv']:
        fpath = data_dir / f
        print(f"  {f}: {'✓' if fpath.exists() else '✗'}")
