"""
MASTER SCRIPT - Complete automated betting analysis workflow
Fetches odds from The Odds API (DraftKings) -> Fetches injuries from RotoWire -> Analyzes props -> Generates betting card

Key features:
- Filter by specific bookmaker (DraftKings recommended)
- Auto-fetch latest injuries from RotoWire
- Auto-opens betting card
- Saves timestamped betting cards with validation forms
"""

import sys
from pathlib import Path
import logging
from datetime import datetime
import pandas as pd
import platform
import subprocess

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Try to use enhanced API, fall back to original
try:
    from scripts.api.odds_api_enhanced import OddsAPI
    USING_ENHANCED = True
except ImportError:
    from scripts.api.odds_api import OddsAPI
    USING_ENHANCED = False

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.enhanced_betting_card import save_betting_card_with_timestamps, BettingCardFormatter

# Try to import injury scraper
try:
    from scripts.fetch_rotowire_injuries import RotoWireInjuryScraper
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False


def open_file(file_path: str):
    """Open file with default application (cross-platform)"""
    try:
        if platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', file_path])
        elif platform.system() == 'Windows':
            subprocess.Popen(['start', file_path], shell=True)
        else:  # Linux
            subprocess.Popen(['xdg-open', file_path])
        print(f"✅ Betting card opened automatically")
    except Exception as e:
        print(f"⚠️ Could not auto-open file: {e}")
        print(f"   Please open manually: {file_path}")


def fetch_latest_injuries(week: int = 8) -> bool:
    """
    Fetch latest injuries from RotoWire
    Returns True if successful, False otherwise
    """
    if not SCRAPER_AVAILABLE:
        print("⚠️ RotoWire scraper not available (install selenium webdriver-manager)")
        return False
    
    print("🏥 FETCHING LATEST INJURIES FROM ROTOWIRE")
    print("-"*70)
    
    try:
        scraper = RotoWireInjuryScraper()
        
        # fetch_injuries() now returns a file path, not a DataFrame
        downloaded_file = scraper.fetch_injuries()
        
        if not downloaded_file:
            print("⚠️ No injuries found (or RotoWire unavailable)")
            return False
        
        # Load the downloaded file
        injuries_df = pd.read_csv(downloaded_file)
        
        if injuries_df.empty:
            print("⚠️ Downloaded file was empty")
            return False
        
        # Save to our project data directory with proper naming
        output_file = project_root / "data" / f"wk{week}-injury-report.csv"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        injuries_df.to_csv(output_file, index=False)
        
        print(f"✅ Fetched {len(injuries_df)} injuries from RotoWire")
        print(f"✅ Saved to: {output_file}")
        print()
        
        return True
    
    except Exception as e:
        print(f"⚠️ Failed to fetch injuries: {e}")
        print("   Proceeding with existing injury data...")
        print()
        return False


def run_complete_analysis(week: int = 8, skip_fetch: bool = False, bookmaker: str = None, 
                         fetch_injuries: bool = True, no_open: bool = False):
    """
    Complete automated workflow:
    1. Optionally fetch latest injuries from RotoWire
    2. Fetch odds from The Odds API (optionally filtered by bookmaker)
    3. Load all DVOA/projection data
    4. Analyze all props
    5. Generate actionable betting card
    6. Auto-open betting card
    
    Args:
        week: NFL week to analyze
        skip_fetch: Skip fetching new odds (use cached)
        bookmaker: Filter to specific bookmaker ('draftkings', 'fanduel', etc.)
        fetch_injuries: Fetch latest injuries from RotoWire
        no_open: Do not auto-open betting card
    """
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*70)
    print("🏈 NFL BETTING ANALYSIS SYSTEM - COMPLETE WORKFLOW")
    print("="*70)
    print(f"Week: {week}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if bookmaker:
        print(f"Bookmaker: {bookmaker.upper()}")
    print("="*70)
    print()
    
    # STEP 0: Fetch injuries (optional)
    if fetch_injuries:
        fetch_latest_injuries(week)
    
    # STEP 1: Fetch odds from API (unless skipped)
    if not skip_fetch:
        print("📡 STEP 1: FETCHING LIVE ODDS FROM THE ODDS API")
        print("-"*70)
        
        try:
            api = OddsAPI()
            
            # Check quota
            quota = api.check_api_quota()
            print(f"API Quota - Remaining: {quota['remaining']}, Used: {quota['used']}")
            
            # Show bookmaker info
            if USING_ENHANCED:
                print(f"Available bookmakers: {', '.join(api.list_available_bookmakers())}")
                if bookmaker:
                    print(f"Filtering to: {bookmaker.upper()}")
            
            # Fetch props with optional bookmaker filtering
            fetch_kwargs = {
                'markets': 'player_pass_tds,player_pass_yds,player_pass_completions,player_pass_attempts,'
                          'player_rush_yds,player_rush_attempts,'
                          'player_receptions,player_reception_yds'
            }
            
            if bookmaker and USING_ENHANCED:
                fetch_kwargs['bookmaker'] = bookmaker
            
            all_props_raw = api.get_player_props(**fetch_kwargs)
            
            if all_props_raw:
                # Save to CSV
                df = pd.DataFrame(all_props_raw)
                df['fetch_time'] = datetime.now().isoformat()
                df['week'] = week
                
                if bookmaker:
                    output_file = project_root / "data" / f"betting_lines_wk_{week}_{bookmaker.lower()}.csv"
                else:
                    output_file = project_root / "data" / f"betting_lines_wk_{week}_live.csv"
                
                df.to_csv(output_file, index=False)
                
                print(f"✅ Fetched {len(df)} props from The Odds API")
                if bookmaker:
                    print(f"✅ Source: {bookmaker.upper()} only")
                print(f"✅ Saved to: {output_file}")
            else:
                print("⚠️ No props fetched. Using existing data...")
                
        except ValueError as e:
            print(f"❌ API Error: {e}")
            print("⚠️ Make sure .env file exists with ODDS_API_KEY")
            print("⚠️ Proceeding with existing data...")
            
        except Exception as e:
            print(f"❌ API fetch failed: {e}")
            print("⚠️ Proceeding with existing data...")
    else:
        print("⏭️  STEP 1: SKIPPED (using existing odds)")
        print("-"*70)
    
    print()
    
    # STEP 2: Load all data
    print("📂 STEP 2: LOADING & TRANSFORMING NFL DATA")
    print("-"*70)
    
    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    context = loader.load_all_data(week=week)
    
    if context.get('props') is None or len(context['props']) == 0:
        print("❌ No props found after loading! Check your data files.")
        print("   Make sure 'wk8_betting_lines_draftkings.csv' or similar exists.")
        return
    
    print(f"✅ Loaded and transformed data for {len(context['props'])} props.")
    print()
    
    # STEP 3: Analyze props
    print("🧠 STEP 3: ANALYZING PROPS")
    print("-"*70)
    
    analyzer = PropAnalyzer()
    analyzed_props = analyzer.analyze_all_props(context, min_confidence=50)
    
    print(f"✅ Analyzed {len(analyzed_props)} props with confidence > 50")
    print()
    
    # STEP 4: Filter high-confidence props
    print("🔄 STEP 4: DIVERSIFYING PROP LIST")
    print("-"*70)
    
    # Sort by confidence and game variety
    analyzed_props_sorted = sorted(analyzed_props, key=lambda p: -p.final_confidence)
    
    print(f"✅ Reordered {len(analyzed_props_sorted)} props for game variety")
    print()
    
    # STEP 5: Build parlays
    print("🎯 STEP 5: BUILDING OPTIMAL PARLAYS")
    print("-"*70)
    print()
    
    builder = ParlayBuilder()
    parlays_dict = builder.build_parlays(
        all_analyses=analyzed_props_sorted,
        min_confidence=52
    )
    
    # Flatten parlays dict to list format
    parlays = []
    for leg_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
        parlays.extend(parlays_dict.get(leg_type, []))
    
    if parlays:
        print(f"✅ Built 10 optimal parlays (from props with 58+ confidence)")
        print()
    else:
        print("❌ Failed to build parlays")
        return
    
    # STEP 6: Generate betting card with timestamped storage
    print("📄 STEP 6: GENERATING BETTING CARD")
    print("-"*70)
    
    # Get formatted betting card
    betting_card_text = builder.format_parlays_for_betting(parlays_dict)
    
    # Save with timestamps and validation form
    card_path, form_path, folder_path = save_betting_card_with_timestamps(
        betting_card=betting_card_text,
        parlays=parlays_dict,
        week=week,
        data_dir=str(project_root / "data")
    )
    
    print(f"✅ Saved betting card to: {card_path}")
    print(f"✅ Saved validation form to: {form_path}")
    print(f"✅ Full folder: {folder_path}")
    print()
    
    # Final summary
    print("="*70)
    print("ANALYSIS COMPLETE!")
    print("="*70)
    print()
    print(f"Generated {len(parlays)} parlays")
    if bookmaker:
        print(f"Source: {bookmaker.upper()}")
    print(f"Betting card: {card_path}")
    print(f"Validation form: {form_path}")
    print()
    
    # Auto-open the betting card (unless disabled)
    if not no_open:
        open_file(card_path)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NFL Betting Analysis System")
    parser.add_argument('--week', type=int, default=8, help='NFL week to analyze')
    parser.add_argument('--skip-fetch', action='store_true', help='Skip fetching new odds (use cached data)')
    parser.add_argument('--bookmaker', type=str, default=None, 
                       help='Filter to specific bookmaker: draftkings, fanduel, pointsbetau, betrivers, etc.')
    parser.add_argument('--no-open', action='store_true', help='Do not auto-open betting card')
    parser.add_argument('--skip-injuries', action='store_true', help='Skip fetching latest injuries from RotoWire')
    
    args = parser.parse_args()
    
    run_complete_analysis(
        week=args.week,
        skip_fetch=args.skip_fetch,
        bookmaker=args.bookmaker,
        fetch_injuries=not args.skip_injuries,
        no_open=args.no_open
    )
