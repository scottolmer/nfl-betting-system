#!/usr/bin/env python
"""Test which Odds API markets are available"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

import requests
import os

api_key = os.getenv('ODDS_API_KEY')
if not api_key:
    print("❌ ODDS_API_KEY not found in .env")
    sys.exit(1)

print("\n" + "="*60)
print("🏈 TESTING ODDS API MARKETS")
print("="*60 + "\n")

# Test 1: Get sports list (free call)
print("1️⃣  Checking available sports...")
try:
    url = "https://api.the-odds-api.com/v4/sports"
    response = requests.get(url, params={'apiKey': api_key})
    sports = response.json()
    
    nfl = [s for s in sports if 'nfl' in s['key'].lower()]
    if nfl:
        print(f"   ✅ NFL sports available:")
        for sport in nfl:
            print(f"      - {sport['key']}: {sport['title']}")
    else:
        print("   ❌ No NFL sports found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Try different market combinations
markets_to_test = [
    "h2h",  # Head to head
    "spreads",
    "totals",
    "player_pass_yds",
    "player_rush_yds",
    "player_receptions",
    "player_pass_tds",
    "player_pass_yds,player_rush_yds",
]

print("\n2️⃣  Testing market availability...")

for market in markets_to_test:
    try:
        url = "https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds"
        params = {
            'apiKey': api_key,
            'regions': 'us',
            'markets': market,
            'oddsFormat': 'american',
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                prop_count = sum(len(e.get('bookmakers', [])) for e in data)
                print(f"   ✅ {market}: {len(data)} events")
            else:
                print(f"   ⚠️  {market}: No data returned")
        else:
            print(f"   ❌ {market}: {response.status_code} - {response.reason}")
            
    except Exception as e:
        print(f"   ❌ {market}: {e}")

print("\n" + "="*60)
