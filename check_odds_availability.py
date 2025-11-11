#!/usr/bin/env python
"""Check what markets are currently available from The Odds API"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.api.odds_api import OddsAPI

print("\n" + "="*60)
print("🔍 CHECKING AVAILABLE NFL MARKETS")
print("="*60)
print()

api = OddsAPI()

# Check for upcoming NFL games
print("1️⃣ Checking for upcoming NFL games...")
try:
    events = api.get_nfl_events()
    if events:
        print(f"   ✅ Found {len(events)} upcoming games:")
        for event in events[:3]:
            print(f"      {event['away_team']} @ {event['home_team']}")
            print(f"      Starts: {event['commence_time']}")
    else:
        print("   ❌ No upcoming NFL games found")
        print("   This is likely because:")
        print("      - NFL season hasn't started yet")
        print("      - We're between game weeks")
        print("      - Season is over")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Try basic h2h odds (always available for scheduled games)
print("2️⃣ Testing basic odds endpoint...")
try:
    import requests
    url = f"{api.base_url}/sports/americanfootball_nfl/odds"
    params = {
        'apiKey': api.api_key,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'american',
    }
    response = api.session.get(url, params=params, timeout=30)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Found {len(data)} games with odds")
    else:
        print(f"   ❌ Error: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Try player props if games exist
if events:
    print("3️⃣ Testing player props availability...")
    try:
        url = f"{api.base_url}/sports/americanfootball_nfl/odds"
        params = {
            'apiKey': api.api_key,
            'regions': 'us',
            'markets': 'player_pass_yds',  # Just one market
            'oddsFormat': 'american',
        }
        response = api.session.get(url, params=params, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Player props available!")
            # Count total props
            total_props = sum(
                len(outcome) 
                for event in data 
                for bookmaker in event.get('bookmakers', [])
                for market in bookmaker.get('markets', [])
                for outcome in market.get('outcomes', [])
            )
            print(f"   Found data for {total_props} prop outcomes")
        elif response.status_code == 422:
            print(f"   ❌ Player props not available (422 error)")
            print(f"   Response: {response.text[:300]}")
        else:
            print(f"   ❌ Error {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print()
print("="*60)
print("RECOMMENDATION:")
print("="*60)

if not events:
    print("No upcoming NFL games - cannot fetch player props.")
    print("The system will use existing CSV data for analysis.")
else:
    print("Games are scheduled. If player props show 422 error:")
    print("  1. Props may not be released yet (usually ~3 days before game)")
    print("  2. Try using DraftKings scraper as backup")
    print("  3. System will fall back to existing CSV data")

print()
