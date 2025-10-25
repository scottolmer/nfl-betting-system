"""
Fetch current NFL betting odds from The Odds API and save to CSV
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import logging

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.api.odds_api import OddsAPI

def fetch_and_save_odds(week: int = 7):
    """
    Fetch odds from The Odds API and save to CSV
    """
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("🏈 FETCHING NFL BETTING ODDS FROM THE ODDS API")
    print("="*60)
    print()
    
    try:
        # Initialize API
        api = OddsAPI()
        
        # Check quota first
        print("📊 Checking API quota...")
        quota = api.check_api_quota()
        print(f"   Requests remaining: {quota['remaining']}")
        print(f"   Requests used: {quota['used']}")
        print()
        
        # Fetch all props (uses 1 API request)
        print(f"📡 Fetching Week {week} player props...")
        print("   This will use 1 API request")
        print()
        
        # Fetch comprehensive prop markets
        all_props = api.get_player_props(
            markets='player_pass_tds,player_pass_yds,player_pass_completions,player_pass_attempts,'
                   'player_rush_yds,player_rush_attempts,'
                   'player_receptions,player_reception_yds'
        )
        
        if not all_props:
            print("❌ No props found!")
            return
        
        print(f"✅ Fetched {len(all_props)} total props")
        print()
        
        # Convert to DataFrame
        df = pd.DataFrame(all_props)
        
        # Add metadata columns
        df['fetch_time'] = datetime.now().isoformat()
        df['week'] = week
        
        # Reorder columns for readability
        columns = [
            'player_name', 'stat_type', 'line', 'direction', 'odds',
            'home_team', 'away_team', 'commence_time',
            'bookmaker', 'market', 'event_id', 'week', 'fetch_time'
        ]
        df = df[columns]
        
        # Save to CSV
        output_file = project_root / "data" / f"betting_lines_wk_{week}_live.csv"
        df.to_csv(output_file, index=False)
        
        print("="*60)
        print("📊 SUMMARY")
        print("="*60)
        print(f"Total props fetched: {len(df)}")
        print(f"Unique players: {df['player_name'].nunique()}")
        print(f"Unique stat types: {df['stat_type'].nunique()}")
        print(f"Unique games: {df['event_id'].nunique()}")
        print()
        
        print("Stat type breakdown:")
        print(df['stat_type'].value_counts().to_string())
        print()
        
        print(f"✅ Saved to: {output_file}")
        print()
        
        # Show sample props
        print("="*60)
        print("🎯 SAMPLE PROPS (Random 5)")
        print("="*60)
        
        sample = df.sample(min(5, len(df)))[['player_name', 'stat_type', 'line', 'direction', 'odds']]
        print(sample.to_string(index=False))
        print()
        
        # Final quota check
        print("="*60)
        print("📊 Final API Status")
        print("="*60)
        final_quota = api.check_api_quota()
        print(f"Requests remaining: {final_quota['remaining']}")
        print(f"Requests used: {final_quota['used']}")
        print()
        
        print("="*60)
        print("✅ Odds fetch complete!")
        print("="*60)
        print()
        print("Next steps:")
        print("  1. Run: python scripts\\generate_betting_card.py")
        print("  2. Review your betting card in data/week7_betting_card.txt")
        print()
        
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        print()
        print("Make sure you have a .env file with:")
        print("ODDS_API_KEY=your_api_key_here")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch NFL betting odds from The Odds API')
    parser.add_argument('--week', type=int, default=7, help='NFL week number')
    
    args = parser.parse_args()
    
    fetch_and_save_odds(week=args.week)
