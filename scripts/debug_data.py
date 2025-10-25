"""
Debug script - Inspect data structure and team name matching
"""

import sys
sys.path.append('.')

from scripts.analysis.data_loader import NFLDataLoader
import pandas as pd

# Load data
loader = NFLDataLoader(data_dir='data')
context = loader.load_all_data(week=8)

print("="*60)
print("DATA LOADED:")
print("="*60)
print(f"DVOA Off: {context['dvoa_off'] is not None}")
print(f"DVOA Def: {context['dvoa_def'] is not None}")
print(f"Def vs WR: {context['def_vs_wr'] is not None}")
print(f"Betting lines: {context['betting_lines'] is not None}")

# Show betting lines structure
if context['betting_lines'] is not None:
    df = context['betting_lines']
    print(f"\n{'='*60}")
    print(f"BETTING LINES COLUMNS:")
    print(f"{'='*60}")
    print(df.columns.tolist())
    
    print(f"\n{'='*60}")
    print(f"SAMPLE BETTING LINES (first 5):")
    print(f"{'='*60}")
    print(df.head())

# Show DVOA offensive structure
if context['dvoa_off'] is not None:
    df = context['dvoa_off']
    print(f"\n{'='*60}")
    print(f"DVOA OFFENSIVE COLUMNS:")
    print(f"{'='*60}")
    print(df.columns.tolist())
    
    print(f"\n{'='*60}")
    print(f"SAMPLE DVOA OFFENSIVE (first 5):")
    print(f"{'='*60}")
    print(df.head())
