#!/usr/bin/env python
"""Check how many UNIQUE PLAYERS are available at different thresholds"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader

loader = NFLDataLoader(data_dir=str(project_root / "data"))
analyzer = PropAnalyzer()

week = 9
print(f"\n📊 Analyzing unique PLAYERS vs total PROPS for Week {week}...\n")

# Load data
context = loader.load_all_data(week=week)
props_list = context.get('props', [])

# Analyze all props
all_analyses = []
for i, prop in enumerate(props_list, 1):
    try:
        analysis = analyzer.analyze_prop(prop, context)
        if analysis:
            all_analyses.append(analysis)
    except Exception as e:
        pass

print(f"Total props analyzed: {len(all_analyses)}\n")

# Check thresholds
thresholds = [50, 55, 60, 65, 70, 75, 80]
print("📊 UNIQUE PLAYERS vs TOTAL PROPS AT EACH THRESHOLD:")
print("="*70)
for threshold in thresholds:
    above = [a for a in all_analyses if a.final_confidence >= threshold]
    unique_players = len(set(a.prop.player_name for a in above))
    print(f"≥ {threshold}%: {len(above):3d} props from {unique_players:3d} unique players")

print("="*70)
