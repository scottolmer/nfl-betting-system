#!/usr/bin/env python
"""Test Claude API integration with week 9 data"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

print("\n" + "="*60)
print("🏈 TESTING CLAUDE API - WEEK 9")
print("="*60 + "\n")

# Test 1: Import all modules
print("1️⃣  Testing imports...")
try:
    from scripts.api.claude_query_handler import ClaudeQueryHandler
    print("   ✅ All modules imported successfully\n")
except Exception as e:
    print(f"   ❌ Import failed: {e}\n")
    sys.exit(1)

# Test 2: Initialize
print("2️⃣  Initializing components...")
try:
    handler = ClaudeQueryHandler()
    print("   ✅ Handler initialized\n")
except Exception as e:
    print(f"   ❌ Initialization failed: {e}\n")
    sys.exit(1)

# Test 3: Parse query
print("3️⃣  Testing query parsing...")
test_query = "Jordan Love 250 pass yards"
parsed = handler.parse_query(test_query)
if parsed:
    print(f"   ✅ Query parsed: {parsed.get('player_name')} {parsed.get('stat_type')} O{parsed.get('line')}\n")
else:
    print("   ❌ Failed to parse query\n")
    sys.exit(1)

# Test 4: Full analysis with WEEK 9
print("4️⃣  Running Week 9 analysis...")
print(f"   Query: {test_query}\n")
try:
    response = handler.query(test_query, week=9)  # WEEK 9
    print("   ✅ Analysis complete\n")
    print("="*60)
    print("📊 WEEK 9 RESPONSE:")
    print("="*60)
    print(response)
    print("="*60)
except Exception as e:
    print(f"   ❌ Analysis failed: {e}\n")
    import traceback
    traceback.print_exc()

print("\n✅ WEEK 9 TEST COMPLETE\n")
