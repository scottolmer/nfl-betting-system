"""
Live Odds API fetcher - fetches and caches player props from The Odds API
"""

import sys
from pathlib import Path
import logging
import pandas as pd
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.api.odds_api import OddsAPI

logging.getLogger('scripts.api.odds_api').setLevel(logging.ERROR)

def fetch_odds_silent(week: int = 8) -> bool:
    """
    Fetch live player props from The Odds API and save to CSV.
    Falls back to existing CSV data if API call fails.
    
    Returns True if data is available (either fresh or cached), False otherwise.
    """
    try:
        data_dir = project_root / "data"
        
        # Try to fetch from Odds API
        try:
            api = OddsAPI()
            props = api.get_player_props()
            
            if props and len(props) > 0:
                # Convert to DataFrame and save
                df = pd.DataFrame(props)
                df['fetch_time'] = datetime.now().isoformat()
                df['week'] = week
                
                output_file = data_dir / f"betting_lines_wk_{week}_live.csv"
                df.to_csv(output_file, index=False)
                
                return True
        except Exception as api_error:
            # API call failed, try to use existing data
            pass
        
        # Check for existing betting lines files (fallback)
        possible_files = [
            data_dir / f"wk{week}_betting_lines_draftkings.csv",
            data_dir / f"wk{week}_betting_lines_TRANSFORMED.csv",
            data_dir / f"betting_lines_wk_{week}_live.csv",
        ]
        
        for filepath in possible_files:
            if filepath.exists():
                return True
        
        return False
        
    except Exception:
        return False


if __name__ == "__main__":
    success = fetch_odds_silent(week=8)
    print("✅ Odds data loaded" if success else "❌ No odds data found")
