#!/usr/bin/env python
"""
Fix all agents - remove manual UNDER inversions since orchestrator now handles it
"""

import re
from pathlib import Path

agents_dir = Path("scripts/analysis/agents")

# Files to fix
agent_files = [
    "dvoa_agent.py",
    "matchup_agent.py",
    "volume_agent.py",
    "game_script_agent.py",
    "trend_agent.py",
    "variance_agent.py",
    "weather_agent.py",
]

# Pattern to find and remove inversion blocks (handles any whitespace)
inversion_pattern = r'\n\s*# INVERT SCORE FOR UNDER BETS\s*\n\s*if prop\.bet_type == ["\']UNDER["\']:\s*\n\s*score = 100 - score\s*'

for agent_file in agent_files:
    filepath = agents_dir / agent_file
    if not filepath.exists():
        print(f"NOT FOUND: {agent_file}")
        continue
    
    try:
        # Read with UTF-8 encoding
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_length = len(content)
        
        # Remove all inversion blocks
        new_content = re.sub(inversion_pattern, '\n', content)
        
        # Count how many were removed
        removed_count = (original_length - len(new_content)) // 80  # rough estimate
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"FIXED: {agent_file}")
    
    except Exception as e:
        print(f"ERROR in {agent_file}: {e}")

print("\nDone! All agents have been cleaned up.")
