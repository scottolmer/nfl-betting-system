#!/usr/bin/env python
"""
Fix indentation errors in agent files
"""

import re
from pathlib import Path

agents_dir = Path("scripts/analysis/agents")

agent_files = [
    "trend_agent.py",
    "variance_agent.py",
    "weather_agent.py",
]

for agent_file in agent_files:
    filepath = agents_dir / agent_file
    if not filepath.exists():
        print(f"NOT FOUND: {agent_file}")
        continue
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix pattern: line starting with "direction = " that should be indented
        # This happens when we removed the INVERT block above it
        content = re.sub(
            r'\n(direction = "OVER")',
            r'\n        \1',
            content
        )
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"FIXED: {agent_file}")
    
    except Exception as e:
        print(f"ERROR in {agent_file}: {e}")

print("\nDone!")
