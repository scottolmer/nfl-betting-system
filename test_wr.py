#!/usr/bin/env python
"""Test WR prop analysis"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.api.claude_query_handler import ClaudeQueryHandler

handler = ClaudeQueryHandler()

# Find a top WR
from scripts.analysis.data_loader import NFLDataLoader
loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=8)

wr_props = [p for p in context.get('props', []) if p.get('position') == 'WR' and 'Rec Yds' in p.get('stat_type', '')]
if wr_props:
    wr = wr_props[0]
    print(f"Testing WR: {wr['player_name']} ({wr['team']}) vs {wr['opponent']}")
    print(f"Stat: {wr['stat_type']} O{wr['line']}\n")
    
    query = f"{wr['player_name'].title()} {wr['line']} {wr['stat_type'].lower()} good bet?"
    response = handler.query(query, week=8)
    print(response)
