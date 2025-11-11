#!/usr/bin/env python
"""Simple test of Claude API integration"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))

# Test 1: Simple query parsing
print("=" * 60)
print("TEST 1: Claude Query Parsing")
print("=" * 60)

prompt = """Parse this betting query and return ONLY valid JSON:

QUERY: "Jordan Love 250 pass yards good bet?"

Return JSON with these fields:
{"player_name": "player", "stat_type": "stat", "line": 250.5, "direction": "OVER", "parsing_valid": true}

Return ONLY the JSON, no other text."""

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=500,
    messages=[{"role": "user", "content": prompt}]
)

result = response.content[0].text
print(f"Raw response:\n{result}\n")

# Clean markdown
cleaned = result.replace('```json', '').replace('```', '').strip()
print(f"Cleaned response:\n{cleaned}\n")

# Try to parse
import json
try:
    parsed = json.loads(cleaned)
    print(f"✅ Successfully parsed JSON:")
    print(f"   Player: {parsed.get('player_name')}")
    print(f"   Stat: {parsed.get('stat_type')}")
    print(f"   Line: {parsed.get('line')}")
    print(f"   Direction: {parsed.get('direction')}")
except json.JSONDecodeError as e:
    print(f"❌ Failed to parse JSON: {e}")

print("\n" + "=" * 60)
print("TEST 2: Claude Analysis Request")
print("=" * 60)

analysis_prompt = """You are an NFL prop betting analyst. Analyze this prop:

Player: Jordan Love
Stat: Pass Yards
Line: 250.5
Direction: OVER
Team: Green Bay Packers
Opponent: Chicago Bears
Week: 8

Provide a brief analysis with:
1. Expected performance
2. Confidence level (0-100)
3. Recommendation (YES/NO/MAYBE)

Keep it to 2-3 sentences."""

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=500,
    messages=[{"role": "user", "content": analysis_prompt}]
)

analysis = response.content[0].text
print(f"Analysis:\n{analysis}\n")

print("=" * 60)
print("✅ Claude API is working!")
print("=" * 60)
