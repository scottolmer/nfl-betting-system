#!/usr/bin/env python
"""Test Claude API integration with all features"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

print("\n" + "="*60)
print("🏈 TESTING CLAUDE API FULL INTEGRATION")
print("="*60 + "\n")

# Test 1: Import all modules
print("1️⃣  Testing imports...")
try:
    from scripts.api.claude_query_handler import ClaudeQueryHandler
    from scripts.analysis.injury_analyzer import InjuryAnalyzer
    from scripts.analysis.matchup_narrative import MatchupNarrativeGenerator
    print("   ✅ All modules imported successfully\n")
except Exception as e:
    print(f"   ❌ Import failed: {e}\n")
    sys.exit(1)

# Test 2: Initialize components
print("2️⃣  Initializing components...")
try:
    handler = ClaudeQueryHandler()
    print("   ✅ ClaudeQueryHandler initialized")
    print("   ✅ InjuryAnalyzer initialized")
    print("   ✅ MatchupNarrativeGenerator initialized\n")
except Exception as e:
    print(f"   ❌ Initialization failed: {e}\n")
    sys.exit(1)

# Test 3: Parse query
print("3️⃣  Testing query parsing...")
test_query = "Jordan Love 250 pass yards good bet?"
parsed = handler.parse_query(test_query)
if parsed:
    print(f"   ✅ Query parsed successfully")
    print(f"      Player: {parsed.get('player_name')}")
    print(f"      Stat: {parsed.get('stat_type')}")
    print(f"      Line: {parsed.get('line')}\n")
else:
    print("   ❌ Failed to parse query\n")
    sys.exit(1)

# Test 4: Full analysis
print("4️⃣  Running full analysis...")
print(f"   Query: {test_query}\n")
try:
    response = handler.query(test_query, week=8)
    print("   ✅ Analysis complete\n")
    print("="*60)
    print("📊 RESPONSE:")
    print("="*60)
    print(response)
    print("="*60)
except Exception as e:
    print(f"   ❌ Analysis failed: {e}\n")
    import traceback
    traceback.print_exc()

print("\n✅ INTEGRATION TEST COMPLETE\n")
