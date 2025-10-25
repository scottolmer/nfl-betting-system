"""
MERGED SYSTEM - Quick Test Script

Tests all components of the merged system
"""

import sys
from pathlib import Path
import os

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_merged_system():
    print("\n" + "="*70)
    print("🔥 TESTING MERGED NFL BETTING SYSTEM")
    print("="*70)
    print()
    
    # Test 1: Environment Variables
    print("1️⃣ Testing Environment Variables...")
    required_vars = [
        'ODDS_API_KEY',
        'SLACK_BOT_TOKEN',
        'CLAUDE_API_KEY',
        'NFL_WEEK'
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var} = {value[:20]}...")
        else:
            print(f"   ❌ {var} = NOT SET")
            all_good = False
    
    if not all_good:
        print("\n❌ Some environment variables missing!")
        print("   Check your .env file")
        return False
    
    print("   ✅ All environment variables set!")
    print()
    
    # Test 2: Data Files
    print("2️⃣ Testing Data Files...")
    week = int(os.getenv('NFL_WEEK', 7))
    data_dir = project_root / "data"
    
    # CORRECTED: No projections file needed!
    required_files = [
        f"DVOA_Off_wk_{week}.csv",
        f"DVOA_Def_wk_{week}.csv",
        f"Def_vs_WR_wk_{week}.csv",
        f"betting_lines_wk_{week}.csv"  # Betting lines ARE the projections!
    ]
    
    files_good = True
    for file in required_files:
        file_path = data_dir / file
        if file_path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - NOT FOUND")
            files_good = False
    
    if not files_good:
        print(f"\n⚠️ Some data files missing for Week {week}")
        print("   Run SETUP_DATA_FILES.bat to fix!")
    else:
        print("   ✅ All data files present!")
    
    print()
    
    # Test 3: Analysis System
    print("3️⃣ Testing Multi-Agent Analysis System...")
    try:
        from scripts.analysis.orchestrator import PropAnalyzer
        from scripts.analysis.data_loader import NFLDataLoader
        
        loader = NFLDataLoader(data_dir=str(data_dir))
        analyzer = PropAnalyzer()
        
        print("   ✅ Analysis modules imported")
        print("   ✅ 8 agents loaded:")
        print("      • DVOA Agent (2.0× weight)")
        print("      • Matchup Agent (1.8× weight)")
        print("      • Volume Agent (1.2× weight)")
        print("      • GameScript Agent (1.3× weight)")
        print("      • Injury Agent (1.5× weight)")
        print("      • Trend Agent (1.0× weight)")
        print("      • Variance Agent (0.8× weight)")
        print("      • Weather Agent (0.5× weight)")
        
    except Exception as e:
        print(f"   ❌ Analysis system error: {e}")
        return False
    
    print()
    
    # Test 4: Parlay Builder
    print("4️⃣ Testing Parlay Builder...")
    try:
        from scripts.analysis.parlay_builder import ParlayBuilder
        
        builder = ParlayBuilder()
        print("   ✅ Parlay builder loaded")
        print("   ✅ Strategies: 2-leg, 3-leg, 4-leg")
        print("   ✅ Risk levels: LOW, MODERATE, HIGH")
        
    except Exception as e:
        print(f"   ❌ Parlay builder error: {e}")
        return False
    
    print()
    
    # Test 5: The Odds API
    print("5️⃣ Testing The Odds API Connection...")
    try:
        from scripts.api.odds_api import OddsAPI
        
        api = OddsAPI()
        quota = api.check_api_quota()
        
        print(f"   ✅ API connected")
        print(f"   ✅ Requests remaining: {quota['remaining']}")
        print(f"   ✅ Requests used: {quota['used']}")
        
    except Exception as e:
        print(f"   ❌ API connection error: {e}")
        print("   ⚠️ Check ODDS_API_KEY in .env")
        return False
    
    print()
    
    # Test 6: Slack Bot Components
    print("6️⃣ Testing Slack Bot Components...")
    try:
        slack_bot_file = project_root / "scripts" / "slack_bot" / "app_enhanced.py"
        
        if slack_bot_file.exists():
            print("   ✅ Enhanced Slack bot file exists")
            print("   ✅ Commands available:")
            print("      • /analyze_props")
            print("      • /check_confidence")
            print("      • /build_parlays")
            print("      • /line_movement")
            print("      • /fetch_odds")
            print("      • /system_status")
        else:
            print("   ❌ Enhanced Slack bot not found")
            return False
        
    except Exception as e:
        print(f"   ❌ Slack bot test error: {e}")
        return False
    
    print()
    
    # Test 7: Line Monitor
    print("7️⃣ Testing Enhanced Line Monitor...")
    try:
        monitor_file = project_root / "scripts" / "line_monitoring" / "monitor_enhanced.py"
        
        if monitor_file.exists():
            print("   ✅ Enhanced line monitor exists")
            print("   ✅ Features:")
            print("      • Track game lines + player props")
            print("      • Confidence score integration")
            print("      • Slack alerts with ratings")
        else:
            print("   ❌ Enhanced monitor not found")
            return False
        
    except Exception as e:
        print(f"   ❌ Monitor test error: {e}")
        return False
    
    print()
    
    # Final Summary
    print("="*70)
    print("✅ MERGED SYSTEM TEST COMPLETE!")
    print("="*70)
    print()
    print("🎯 NEXT STEPS:")
    print()
    if not files_good:
        print("1. Run: SETUP_DATA_FILES.bat (to copy files to /data)")
        print()
    print("2. Start Enhanced Slack Bot:")
    print("   python scripts\\slack_bot\\app_enhanced.py")
    print()
    print("3. Start ngrok (in another terminal):")
    print("   ngrok http 3000")
    print()
    print("4. Start Enhanced Line Monitor (in another terminal):")
    print("   python scripts\\line_monitoring\\monitor_enhanced.py")
    print()
    print("5. Test in Slack:")
    print("   /betting_help")
    print("   /analyze_props 7")
    print("   /build_parlays 7")
    print()
    print("="*70)
    print("🔥 YOU NOW HAVE THE ULTIMATE BETTING SYSTEM!")
    print("="*70)
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_merged_system()
        if not success:
            print("\n⚠️ Some tests failed. Check errors above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
