#!/usr/bin/env python
"""Debug GameScript agent"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.agents.game_script_agent import GameScriptAgent

loader = NFLDataLoader(data_dir=str(project_root / "data"))
context = loader.load_all_data(week=8)

# Find Jordan Love prop
for prop in context.get('props', []):
    if 'jordan love' in prop.get('player_name', '').lower():
        print(f"Prop data for GameScript:")
        print(f"  game_total: {prop.get('game_total')}")
        print(f"  spread: {prop.get('spread')}")
        print(f"  is_home: {prop.get('is_home')}")
        print(f"  position: {prop.get('position')}")
        
        # Create a mock Prop object
        class MockProp:
            pass
        mock = MockProp()
        for k, v in prop.items():
            setattr(mock, k, v)
        
        agent = GameScriptAgent()
        score, direction, rationale = agent.analyze(mock, context)
        print(f"\nGameScript result:")
        print(f"  score: {score}")
        print(f"  direction: {direction}")
        print(f"  rationale: {rationale}")
        break
