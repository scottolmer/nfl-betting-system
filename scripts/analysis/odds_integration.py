"""
Odds Integration for Parlay Optimizer
Fetches live betting lines from The Odds API and integrates with parlay generation
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import pandas as pd
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.odds_api_enhanced import OddsAPI

logger = logging.getLogger(__name__)


class OddsIntegrator:
    """Integrates live Odds API data with parlay generation"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize Odds Integrator
        
        Args:
            data_dir: Directory to cache odds data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.bookmaker = "draftkings"
        self.api = None
        self.last_fetch_time = None
        self.cached_props = []
        
        try:
            self.api = OddsAPI()
            logger.info(f"✅ Odds API initialized (DraftKings only)")
        except ValueError as e:
            logger.warning(f"⚠️ Odds API key not configured: {e}")
            logger.info("   Will fall back to cached CSV data")
    
    def fetch_live_odds(self, week: int = None, use_cache: bool = True) -> Tuple[List[Dict], str]:
        """
        Fetch live odds from The Odds API with fallback to cached data
        
        Args:
            week: NFL week number (optional, for logging)
            use_cache: If True, fall back to cached CSV if API fails
        
        Returns:
            Tuple of (props_list, source) where source is "LIVE" or "CACHED"
        """
        
        # Try to fetch from live API
        if self.api:
            try:
                logger.info(f"📡 Fetching live DraftKings odds from The Odds API...")
                
                props = self.api.get_player_props(
                    bookmaker='draftkings',
                    markets='player_pass_tds,player_pass_yds,player_rush_yds,player_receptions,player_reception_yds,player_touchdowns'
                )
                
                if props and len(props) > 0:
                    logger.info(f"✅ Fetched {len(props)} live props from DraftKings")
                    
                    # Cache to CSV
                    if week:
                        self._cache_props_to_csv(props, week)
                    
                    self.cached_props = props
                    self.last_fetch_time = datetime.now()
                    
                    return props, "LIVE"
                else:
                    logger.warning("⚠️ API returned no props, falling back to cache")
            
            except Exception as e:
                logger.warning(f"⚠️ Odds API fetch failed: {e}")
                logger.info("   Falling back to cached data")
        
        # Fall back to cached CSV data
        if use_cache:
            cached_props = self._load_cached_props(week)
            if cached_props:
                logger.info(f"📂 Using cached props: {len(cached_props)} lines")
                return cached_props, "CACHED"
        
        logger.error("❌ No props available (no API key and no cached data)")
        return [], "NONE"
    
    def _cache_props_to_csv(self, props: List[Dict], week: int):
        """Cache props to CSV file"""
        try:
            df = pd.DataFrame(props)
            df['fetch_time'] = datetime.now().isoformat()
            df['week'] = week
            df['source'] = self.bookmaker
            
            # Save to betting_lines_wk_{week}_live.csv
            output_file = self.data_dir / f"betting_lines_wk_{week}_{self.bookmaker}_live.csv"
            df.to_csv(output_file, index=False)
            
            logger.info(f"💾 Cached {len(props)} props to {output_file.name}")
        
        except Exception as e:
            logger.warning(f"⚠️ Failed to cache props to CSV: {e}")
    
    def _load_cached_props(self, week: Optional[int] = None) -> List[Dict]:
        """Load cached props from CSV"""
        try:
            # Try week-specific files first
            if week:
                possible_files = [
                    self.data_dir / f"betting_lines_wk_{week}_{self.bookmaker}_live.csv",
                    self.data_dir / f"betting_lines_wk_{week}_live.csv",
                    self.data_dir / f"wk{week}_betting_lines_draftkings.csv",
                    self.data_dir / f"wk{week}_betting_lines_TRANSFORMED.csv",
                ]
            else:
                # Find most recent betting lines file
                possible_files = sorted(
                    self.data_dir.glob("betting_lines*.csv"),
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )[:5]  # Check 5 most recent
            
            for filepath in possible_files:
                if filepath.exists():
                    try:
                        df = pd.read_csv(filepath)
                        props = df.to_dict('records')
                        logger.info(f"✅ Loaded {len(props)} cached props from {filepath.name}")
                        return props
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to read {filepath.name}: {e}")
                        continue
            
            logger.warning("⚠️ No cached props found")
            return []
        
        except Exception as e:
            logger.warning(f"⚠️ Error loading cached props: {e}")
            return []
    
    def enrich_props_with_odds(self, props: List[Dict], live_odds: List[Dict]) -> List[Dict]:
        """
        Enrich analysis props with live betting lines
        
        Args:
            props: Original props from data loader
            live_odds: Props fetched from Odds API
        
        Returns:
            Enriched props with live odds data
        """
        
        # Create lookup dict keyed by (player, stat_type, direction, line)
        odds_lookup = {}
        for odd in live_odds:
            key = (
                odd.get('player_name', '').lower().strip(),
                odd.get('stat_type', '').lower().strip(),
                odd.get('direction', '').lower().strip(),
                round(float(odd.get('line', 0)), 1)
            )
            odds_lookup[key] = odd
        
        # Enrich props
        enriched = []
        for prop in props:
            key = (
                prop.get('player_name', '').lower().strip(),
                prop.get('stat_type', '').lower().strip(),
                prop.get('direction', 'over').lower().strip(),
                round(float(prop.get('line', 0)), 1)
            )
            
            if key in odds_lookup:
                # Found live odds for this prop
                live_odd = odds_lookup[key]
                prop['live_odds'] = live_odd.get('odds')
                prop['live_line'] = live_odd.get('line')
                prop['bookmaker'] = live_odd.get('bookmaker', 'unknown')
                prop['odds_source'] = 'LIVE'
            else:
                # Use cached/estimated odds
                prop['odds_source'] = 'CACHED'
            
            enriched.append(prop)
        
        return enriched
    
    def get_api_quota(self) -> Dict:
        """Get current API quota"""
        if self.api:
            try:
                return self.api.check_api_quota()
            except Exception as e:
                logger.warning(f"Failed to check quota: {e}")
                return {'remaining': 'Unknown', 'used': 'Unknown'}
        
        return {'remaining': 'N/A', 'used': 'N/A', 'note': 'No API key configured'}
    
    def print_odds_status(self):
        """Print current odds integration status"""
        quota = self.get_api_quota()
        
        print("\n" + "="*70)
        print("📊 ODDS API STATUS")
        print("="*70)
        print(f"Status:         {'✅ CONNECTED' if self.api else '❌ NO API KEY'}")
        print(f"Bookmaker:      DraftKings")
        print(f"Last fetch:     {self.last_fetch_time if self.last_fetch_time else 'Never'}")
        print(f"Cached props:   {len(self.cached_props)}")
        print(f"API Remaining:  {quota.get('remaining', 'Unknown')}")
        print(f"API Used:       {quota.get('used', 'Unknown')}")
        print("="*70 + "\n")


def integrate_odds_with_analysis(
    original_props: List[Dict],
    week: int = None,
    data_dir: str = "data"
) -> Tuple[List[Dict], str]:
    """
    High-level function to integrate live DraftKings odds with prop analysis
    
    Args:
        original_props: Props from data loader
        week: NFL week number
        data_dir: Data directory path
    
    Returns:
        Tuple of (enriched_props, source) where source is "LIVE" or "CACHED"
    """
    
    integrator = OddsIntegrator(data_dir=data_dir)
    
    # Fetch live odds (with fallback)
    live_odds, source = integrator.fetch_live_odds(week=week, use_cache=True)
    
    # Enrich props with live odds
    if live_odds:
        enriched_props = integrator.enrich_props_with_odds(original_props, live_odds)
        logger.info(f"✅ Enriched {len(enriched_props)} props with {source} DraftKings odds data")
        return enriched_props, source
    else:
        logger.warning("⚠️ No live or cached odds available, using original props")
        return original_props, "NONE"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*70)
    print("🏈 ODDS API INTEGRATION TEST")
    print("="*70 + "\n")
    
    integrator = OddsIntegrator()
    
    # Test fetch
    props, source = integrator.fetch_live_odds(week=10)
    print(f"\n✅ Fetch successful: {len(props)} props from {source}")
    
    # Print status
    integrator.print_odds_status()
    
    if props:
        print("\n📊 Sample props:")
        for prop in props[:3]:
            print(f"   {prop.get('player_name')}: {prop.get('stat_type')} {prop.get('direction')} {prop.get('line')}")
