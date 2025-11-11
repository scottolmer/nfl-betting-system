#!/usr/bin/env python
"""Quick verification that Odds API integration is working"""

import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

print("\n" + "="*60)
print("🏈 ODDS API INTEGRATION VERIFICATION")
print("="*60 + "\n")

# Check 1: API Key
print("1️⃣  Checking for ODDS_API_KEY...")
import os
api_key = os.getenv('ODDS_API_KEY')
if api_key:
    print(f"   ✅ Found: {api_key[:10]}...")
else:
    print("   ❌ ODDS_API_KEY not found in .env")
    print("   Add: ODDS_API_KEY=your_api_key_here\n")
    sys.exit(1)

# Check 2: OddsAPI class import
print("\n2️⃣  Testing OddsAPI import...")
try:
    from scripts.api.odds_api import OddsAPI
    print("   ✅ OddsAPI imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import: {e}\n")
    sys.exit(1)

# Check 3: Initialize API
print("\n3️⃣  Initializing Odds API client...")
try:
    api = OddsAPI()
    print("   ✅ API client initialized")
except Exception as e:
    print(f"   ❌ Failed to initialize: {e}\n")
    sys.exit(1)

# Check 4: Check quota
print("\n4️⃣  Checking API quota...")
try:
    quota = api.check_api_quota()
    print(f"   ✅ Requests remaining: {quota['remaining']}")
    print(f"   ✅ Requests used: {quota['used']}")
except Exception as e:
    print(f"   ❌ Failed to check quota: {e}\n")
    sys.exit(1)

# Check 5: Fetch props
print("\n5️⃣  Fetching live player props...")
try:
    props = api.get_player_props()
    print(f"   ✅ Successfully fetched {len(props)} props")
    
    if props:
        sample = props[0]
        print(f"\n   Sample prop:")
        print(f"      Player: {sample['player_name']}")
        print(f"      Stat: {sample['stat_type']}")
        print(f"      Line: {sample['line']}")
        print(f"      Direction: {sample['direction']}")
except Exception as e:
    print(f"   ❌ Failed to fetch props: {e}\n")
    sys.exit(1)

# Check 6: Save to CSV
print("\n6️⃣  Testing CSV save...")
try:
    import pandas as pd
    from datetime import datetime
    
    df = pd.DataFrame(props)
    df['fetch_time'] = datetime.now().isoformat()
    
    output_file = Path("data") / "test_odds_fetch.csv"
    df.to_csv(output_file, index=False)
    print(f"   ✅ Saved test data to {output_file}")
except Exception as e:
    print(f"   ❌ Failed to save CSV: {e}\n")
    sys.exit(1)

# Check 7: Test new CLI
print("\n7️⃣  Checking new CLI file...")
try:
    cli_file = Path("betting_cli_odds_integrated.py")
    if cli_file.exists():
        print(f"   ✅ Found: {cli_file}")
    else:
        print(f"   ❌ Not found: {cli_file}\n")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL CHECKS PASSED!")
print("="*60)
print("\nNext steps:")
print("  1. Run: python betting_cli_odds_integrated.py")
print("  2. Type: analyze Jordan Love 275 pass yards")
print("  3. Check quota: odds command")
print("\n")
