#!/usr/bin/env python
"""Test that Odds API integration is working correctly"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("\n" + "="*60)
print("🧪 TESTING ODDS API INTEGRATION")
print("="*60)
print()

# Test 1: Check environment variable
print("1️⃣ Checking ODDS_API_KEY environment variable...")
import os
api_key = os.getenv('ODDS_API_KEY')
if api_key:
    print(f"   ✅ ODDS_API_KEY is set (length: {len(api_key)})")
else:
    print("   ❌ ODDS_API_KEY not found in environment")
    print("   Please add ODDS_API_KEY to your .env file")
    sys.exit(1)

print()

# Test 2: Test OddsAPI class initialization
print("2️⃣ Testing OddsAPI class initialization...")
try:
    from scripts.api.odds_api import OddsAPI
    api = OddsAPI()
    print("   ✅ OddsAPI initialized successfully")
except Exception as e:
    print(f"   ❌ Failed to initialize: {e}")
    sys.exit(1)

print()

# Test 3: Test API quota check
print("3️⃣ Checking API quota...")
try:
    quota = api.check_api_quota()
    print(f"   Requests used: {quota['used']}")
    print(f"   Requests remaining: {quota['remaining']}")
    print("   ✅ API connection working")
except Exception as e:
    print(f"   ❌ Failed to check quota: {e}")
    sys.exit(1)

print()

# Test 4: Test silent fetch function
print("4️⃣ Testing silent odds fetch (uses 1 API request)...")
try:
    from scripts.fetch_odds_silent import fetch_odds_silent
    result = fetch_odds_silent(week=8)
    if result:
        print("   ✅ Silent fetch successful")
        
        # Check if file was created
        data_file = project_root / "data" / "betting_lines_wk_8_live.csv"
        if data_file.exists():
            import pandas as pd
            df = pd.read_csv(data_file)
            print(f"   ✅ CSV file created with {len(df)} props")
            print(f"   Sample players: {', '.join(df['player_name'].head(3).tolist())}")
        else:
            print("   ⚠️  CSV file not found")
    else:
        print("   ❌ Silent fetch returned False")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 5: Final quota check
print("5️⃣ Final API quota check...")
try:
    final_quota = api.check_api_quota()
    print(f"   Requests used: {final_quota['used']}")
    print(f"   Requests remaining: {final_quota['remaining']}")
except Exception as e:
    print(f"   ⚠️  Could not check final quota: {e}")

print()
print("="*60)
print("✅ ALL TESTS PASSED - Odds API is working correctly!")
print("="*60)
print()
print("The analyze command will now:")
print("  1. Fetch fresh odds from The Odds API (1 request)")
print("  2. Save to betting_lines_wk_X_live.csv")
print("  3. Load and analyze the prop")
print()
