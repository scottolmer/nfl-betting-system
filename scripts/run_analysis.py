"""
MASTER SCRIPT - Complete automated betting analysis workflow
Fetches odds -> Analyzes props -> Generates betting card
"""

import sys
from pathlib import Path
import logging
from datetime import datetime
import pandas as pd

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.api.odds_api import OddsAPI
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder


def run_complete_analysis(week: int = 7, skip_fetch: bool = False):
    """
    Complete automated workflow:
    1. Fetch odds from The Odds API
    2. Load all DVOA/projection data
    3. Analyze all props
    4. Generate actionable betting card
    """
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*70)
    print("🏈 NFL BETTING ANALYSIS SYSTEM - COMPLETE WORKFLOW")
    print("="*70)
    print(f"Week: {week}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print()
    
    # STEP 1: Fetch odds from API (unless skipped)
    if not skip_fetch:
        print("📡 STEP 1: FETCHING LIVE ODDS FROM THE ODDS API")
        print("-"*70)
        
        try:
            api = OddsAPI()
            
            # Check quota
            quota = api.check_api_quota()
            print(f"API Quota - Remaining: {quota['remaining']}, Used: {quota['used']}")
            
            # Fetch props (uses 1 API request)
            all_props_raw = api.get_player_props(
                markets='player_pass_tds,player_pass_yds,player_pass_completions,player_pass_attempts,'
                       'player_rush_yds,player_rush_attempts,'
                       'player_receptions,player_reception_yds'
            )
            
            if all_props_raw:
                # Save to CSV
                df = pd.DataFrame(all_props_raw)
                df['fetch_time'] = datetime.now().isoformat()
                df['week'] = week
                
                output_file = project_root / "data" / f"betting_lines_wk_{week}_live.csv"
                df.to_csv(output_file, index=False)
                
                print(f"✅ Fetched {len(df)} props from The Odds API")
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
    # This one call now does EVERYTHING: loads files AND transforms them
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
    # We analyze ALL props > 50 confidence
    all_analyses = analyzer.analyze_all_props(context, min_confidence=50)
    
    print(f"✅ Analyzed {len(all_analyses)} props with confidence > 50")
    print()
    
    # STEP 4: Diversify for parlay building
    print("🔄 STEP 4: DIVERSIFYING PROP LIST")
    print("-"*70)
    
    if len(all_analyses) == 0:
        print("⚠️ WARNING: No props met confidence threshold (50+)")
        print("   Lowering to 40 for system test...")
        all_analyses = analyzer.analyze_all_props(context, min_confidence=40)
        if len(all_analyses) == 0:
            print("❌ Still no props. Check data files and player name matching.")
            return
    
    diversified_analyses = diversify_props(all_analyses)
    print(f"✅ Reordered {len(diversified_analyses)} props for game variety")
    print()
    
    # STEP 5: Build parlays
    print("🎯 STEP 5: BUILDING OPTIMAL PARLAYS")
    print("-"*70)
    
    parlay_builder = ParlayBuilder()
    
    # We use min_confidence=52 here, which is our threshold for betting
    parlays = parlay_builder.build_parlays(diversified_analyses, min_confidence=52)
    
    total_parlays = sum(len(p) for p in parlays.values())
    print(f"✅ Built {total_parlays} optimal parlays (from props with 58+ confidence)")
    print()
    
    # STEP 6: Generate betting card
    print("📄 STEP 6: GENERATING BETTING CARD")
    print("-"*70)
    
    betting_card = parlay_builder.format_parlays_for_betting(parlays)
    
    # Save to file
    output_file = project_root / "data" / f"week{week}_betting_card.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(betting_card)
    
    print(f"✅ Saved betting card to: {output_file}")
    print()
    
    # STEP 7: Display results
    print("="*70)
    print("🎉 ANALYSIS COMPLETE!")
    print("="*70)
    print()
    print(betting_card)
    
    # Quick summary
    print("\n" + "="*70)
    print("📊 FINAL SUMMARY")
    print("="*70)
    
    total_2leg = len(parlays.get('2-leg', []))
    total_3leg = len(parlays.get('3-leg', []))
    total_4leg = len(parlays.get('4-leg', []))
    
    print(f"2-leg parlays: {total_2leg}")
    print(f"3-leg parlays: {total_3leg}")
    print(f"4-leg parlays: {total_4leg}")
    print(f"Total parlays: {total_2leg + total_3leg + total_4leg}")
    
    # Calculate total units
    total_units = sum(parlay.recommended_units for parlay_list in parlays.values() for parlay in parlay_list)
    
    print(f"\nTotal recommended units: {total_units:.1f}")
    print(f"At $10/unit: ${total_units * 10:.0f}")
    print(f"At $25/unit: ${total_units * 25:.0f}")
    
    print()
    print("="*70)
    print("🏈 Ready to bet! Good luck!")
    print("="*70)


def diversify_props(all_analyses, min_per_game=5):
    """
    Reorder props to ensure game diversity.
    Takes top props from each game in round-robin fashion.
    """
    # Group by game
    games = {}
    for analysis in all_analyses:
        game = f"{analysis.prop.team} vs {analysis.prop.opponent}"
        if game not in games:
            games[game] = []
        games[game].append(analysis)
    
    # Sort each game's props by confidence
    for game in games:
        games[game].sort(key=lambda x: x.final_confidence, reverse=True)
    
    # Round-robin selection
    diversified = []
    max_rounds = max(len(props) for props in games.values()) if games else 0
    
    for round_num in range(max_rounds):
        for game, props in sorted(games.items(), key=lambda x: len(x[1]), reverse=True):
            if round_num < len(props):
                diversified.append(props[round_num])
    
    return diversified


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run complete NFL betting analysis')
    parser.add_argument('--week', type=int, default=7, help='NFL week number')
    parser.add_argument('--skip-fetch', action='store_true', help='Skip API fetch, use existing data')
    
    args = parser.parse_args()
    
    run_complete_analysis(week=args.week, skip_fetch=args.skip_fetch)