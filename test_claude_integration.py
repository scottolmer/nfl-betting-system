#!/usr/bin/env python3
"""
Test Claude preprocessing and query handler
"""
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('C:\\Users\\scott\\Desktop\\nfl-betting-systemv2\\.env')


# Test 1: Verify ANTHROPIC_API_KEY is set
print("="*70)
print("TEST 1: Environment Setup")
print("="*70)

api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key:
    print("✅ ANTHROPIC_API_KEY found")
else:
    print("❌ ANTHROPIC_API_KEY not set in environment")
    print("   Add to .env file: ANTHROPIC_API_KEY=your_key_here")
    exit(1)

# Test 2: Import preprocessor
print("\n" + "="*70)
print("TEST 2: Import Claude Preprocessor")
print("="*70)

try:
    from scripts.api.claude_preprocessor import ClaudePreprocessor
    print("✅ ClaudePreprocessor imported successfully")
    preprocessor = ClaudePreprocessor()
    print("✅ ClaudePreprocessor instantiated")
except Exception as e:
    print(f"❌ Failed to import: {e}")
    exit(1)

# Test 3: Sample injury data normalization
print("\n" + "="*70)
print("TEST 3: Injury Data Preprocessing")
print("="*70)

sample_injury = """Player,Team,Pos,Injury,Status,Est. Return
Jordan Love,GB,QB,Shoulder,Active,N/A
Marvin Harrison Jr.,ARI,WR,Knee - ACL,Questionable,Week 9
Travis Kelce,KC,TE,Illness,Active,N/A
Patrick Mahomes,KC,QB,Ankle,Doubtful,Week 9"""

print(f"Input: {len(sample_injury)} chars of injury data")
try:
    result = preprocessor.preprocess_injury_data(sample_injury)
    print(f"✅ Injury preprocessing completed")
    print(f"   Parsed {len(result.get('injuries', []))} players")
    for player in result.get('injuries', [])[:2]:
        print(f"   • {player['player_name']} ({player['team']}) - {player['status']}")
except Exception as e:
    print(f"❌ Preprocessing failed: {e}")

# Test 4: Import query handler
print("\n" + "="*70)
print("TEST 4: Import Claude Query Handler")
print("="*70)

try:
    from scripts.api.claude_query_handler import ClaudeQueryHandler
    print("✅ ClaudeQueryHandler imported successfully")
    handler = ClaudeQueryHandler()
    print("✅ ClaudeQueryHandler instantiated")
except Exception as e:
    print(f"❌ Failed to import: {e}")
    exit(1)

# Test 5: Parse natural language query
print("\n" + "="*70)
print("TEST 5: Query Parsing")
print("="*70)

test_query = "Jordan Love 250 pass yards good bet?"
print(f"Input: '{test_query}'")

try:
    parsed = handler.parse_query(test_query)
    if parsed:
        print(f"✅ Query parsed successfully")
        print(f"   Player: {parsed['player_name']}")
        print(f"   Stat: {parsed['stat_type']}")
        print(f"   Line: {parsed['line']}")
        print(f"   Direction: {parsed['direction']}")
    else:
        print("❌ Query parsing returned None")
except Exception as e:
    print(f"❌ Query parsing failed: {e}")

# Test 6: Full query analysis
print("\n" + "="*70)
print("TEST 6: Full Query Analysis")
print("="*70)

print("Running full analysis (this may take 30-60 seconds)...")
try:
    response = handler.query(test_query, week=8)
    print("✅ Full analysis completed")
    print("\nResponse:")
    print(response[:500] + ("...[truncated]" if len(response) > 500 else ""))
except Exception as e:
    print(f"❌ Full analysis failed: {e}")

print("\n" + "="*70)
print("TESTS COMPLETE")
print("="*70)
print("\nNext steps:")
print("1. If all tests passed, bot is ready")
print("2. Run: python scripts/slack_bot/app_with_claude.py")
print("3. In Slack: /ask Jordan Love 250 pass yards good bet?")
