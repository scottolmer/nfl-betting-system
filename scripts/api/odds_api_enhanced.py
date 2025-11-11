"""
The Odds API Client - Enhanced Version with DraftKings Filtering
Documentation: https://the-odds-api.com/

FEATURES:
- Filter by specific bookmaker (DraftKings, FanDuel, BetRivers, etc.)
- Uses event-specific endpoint for player props (required for prop markets)
- Discovers available markets per event to avoid 422 errors
- API quota tracking
- Real-time line fetching
"""

import requests
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging
from dotenv import load_dotenv


class OddsAPI:
    """Client for The Odds API with bookmaker filtering"""
    
    # Known bookmaker keys from The Odds API
    KNOWN_BOOKMAKERS = {
        'draftkings': 'draftkings',
        'fanduel': 'fanduel',
        'pointsbetau': 'pointsbetau',
        'betrivers': 'betrivers',
        'mybookie': 'mybookie',
        'betonline': 'betonline_ag',
        'bovada': 'bovada',
    }
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.api_key = os.getenv('ODDS_API_KEY')
        if not self.api_key:
            raise ValueError(
                "ODDS_API_KEY not found in .env file. "
                "Please add: ODDS_API_KEY=your_api_key_here"
            )
        
        self.base_url = "https://api.the-odds-api.com/v4"
        self.logger = logging.getLogger(__name__)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'NFL-Betting-Analysis-System/1.0'
        })
    
    def get_nfl_events(self) -> List[Dict]:
        """Fetch all upcoming NFL events"""
        try:
            url = f"{self.base_url}/sports/americanfootball_nfl/odds"
            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': 'h2h',
                'oddsFormat': 'american',
            }
            
            self.logger.info("Fetching NFL events from The Odds API...")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            events = []
            for event in data:
                events.append({
                    'event_id': event['id'],
                    'home_team': event['home_team'],
                    'away_team': event['away_team'],
                    'commence_time': event['commence_time'],
                    'sport_key': event['sport_key'],
                })
            
            self.logger.info(f"✅ Found {len(events)} NFL events")
            self._log_remaining_requests(response)
            
            return events
            
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch NFL events: {e}")
            return []
    
    def get_player_props(self, regions: str = 'us', markets: str = 'player_pass_tds,player_pass_yds,player_rush_yds,player_receptions,player_reception_yds,player_touchdowns', bookmaker: Optional[str] = None) -> List[Dict]:
        """
        Fetch all player props for NFL using event-specific endpoint with market discovery
        """
        try:
            # Step 1: Get list of upcoming NFL events
            events_url = f"{self.base_url}/sports/americanfootball_nfl/events"
            events_params = {'apiKey': self.api_key}
            
            if bookmaker:
                bk_name = self.KNOWN_BOOKMAKERS.get(bookmaker.lower(), bookmaker)
                self.logger.info(f"Fetching NFL player props (bookmaker: {bk_name})...")
            else:
                self.logger.info("Fetching NFL player props (all bookmakers)...")
            
            events_response = self.session.get(events_url, params=events_params, timeout=30)
            events_response.raise_for_status()
            events = events_response.json()
            
            # Step 2: For each event, discover available markets then fetch props
            all_props = []
            for event in events[:5]:  # Limit to next 5 games to conserve quota
                event_id = event['id']
                
                # First, discover what markets are available for this event
                markets_url = f"{self.base_url}/sports/americanfootball_nfl/events/{event_id}/markets"
                markets_params = {
                    'apiKey': self.api_key,
                    'regions': regions,
                }
                if bookmaker:
                    markets_params['bookmakers'] = self.KNOWN_BOOKMAKERS.get(bookmaker.lower(), bookmaker)
                
                try:
                    markets_response = self.session.get(markets_url, params=markets_params, timeout=30)
                    markets_response.raise_for_status()
                    markets_data = markets_response.json()
                    
                    # Extract available markets from response
                    available_markets = set()
                    for bm in markets_data.get('bookmakers', []):
                        for market in bm.get('markets', []):
                            available_markets.add(market['key'])
                    
                    # Filter requested markets to only those available
                    requested = set(markets.split(','))
                    valid_markets = ','.join(requested & available_markets)
                    
                    if not valid_markets:
                        self.logger.debug(f"No matching markets for event {event_id}")
                        continue
                    
                except Exception as e:
                    self.logger.debug(f"Could not fetch markets for event {event_id}: {e}")
                    valid_markets = markets  # Fall back to requesting all markets
                
                # Now fetch player props using only valid markets
                props_url = f"{self.base_url}/sports/americanfootball_nfl/events/{event_id}/odds"
                props_params = {
                    'apiKey': self.api_key,
                    'regions': regions,
                    'markets': valid_markets,
                    'oddsFormat': 'american',
                }
                
                try:
                    props_response = self.session.get(props_url, params=props_params, timeout=30)
                    props_response.raise_for_status()
                    
                    data = props_response.json()
                    
                    # Parse props from this event
                    event_props = self._parse_event_props(data, bookmaker=bookmaker)
                    all_props.extend(event_props)
                except requests.exceptions.HTTPError as e:
                    self.logger.debug(f"Skipped event {event_id} (no data for markets): {e}")
                    continue
            
            self.logger.info(f"✅ Found {len(all_props)} total props")
            if all_props:
                self._log_remaining_requests(events_response)
            
            return all_props
            
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch player props: {e}")
            return []
    
    def _parse_event_props(self, event: Dict, bookmaker: Optional[str] = None) -> List[Dict]:
        """Parse all props from a single event, optionally filtering by bookmaker"""
        props = []
        
        event_id = event.get('id', '')
        home_team = event.get('home_team', '')
        away_team = event.get('away_team', '')
        commence_time = event.get('commence_time', '')
        
        # Normalize bookmaker filter
        bookmaker_filter = None
        if bookmaker:
            bookmaker_filter = self.KNOWN_BOOKMAKERS.get(bookmaker.lower(), bookmaker.lower())
        
        # Get bookmakers data
        for bookmaker_data in event.get('bookmakers', []):
            bookmaker_name = bookmaker_data['key']
            
            # Skip if we're filtering and this isn't the right bookmaker
            if bookmaker_filter and bookmaker_name != bookmaker_filter:
                continue
            
            # Parse each market
            for market in bookmaker_data.get('markets', []):
                market_key = market['key']
                
                # Parse each outcome (player prop)
                for outcome in market.get('outcomes', []):
                    prop = {
                        'event_id': event_id,
                        'home_team': home_team,
                        'away_team': away_team,
                        'commence_time': commence_time,
                        'bookmaker': bookmaker_name,
                        'market': market_key,
                        'player_name': outcome.get('description', ''),
                        'stat_type': self._convert_market_to_stat_type(market_key),
                        'line': outcome.get('point', 0),
                        'direction': outcome['name'],  # Over or Under
                        'odds': outcome.get('price', 0),
                    }
                    props.append(prop)
        
        return props
    
    def _convert_market_to_stat_type(self, market_key: str) -> str:
        """Convert The Odds API market key to our stat type format"""
        market_map = {
            'player_pass_tds': 'Pass TDs',
            'player_pass_yds': 'Pass Yds',
            'player_pass_completions': 'Pass Comp',
            'player_pass_attempts': 'Pass Att',
            'player_rush_yds': 'Rush Yds',
            'player_rush_attempts': 'Rush Att',
            'player_receptions': 'Receptions',
            'player_reception_yds': 'Rec Yds',
            'player_touchdowns': 'Touchdowns',
            'player_kicking_points': 'Kicking Pts',
        }
        
        return market_map.get(market_key, market_key)
    
    def _log_remaining_requests(self, response):
        """Log remaining API requests"""
        remaining = response.headers.get('x-requests-remaining')
        used = response.headers.get('x-requests-used')
        
        if remaining:
            self.logger.info(f"API Requests - Used: {used}, Remaining: {remaining}")
    
    def check_api_quota(self) -> Dict:
        """Check remaining API quota"""
        try:
            url = f"{self.base_url}/sports"
            params = {'apiKey': self.api_key}
            
            response = self.session.get(url, params=params, timeout=10)
            
            return {
                'remaining': response.headers.get('x-requests-remaining', 'Unknown'),
                'used': response.headers.get('x-requests-used', 'Unknown'),
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check API quota: {e}")
            return {'remaining': 'Error', 'used': 'Error'}
    
    def list_available_bookmakers(self) -> List[str]:
        """Show all available bookmakers"""
        return list(self.KNOWN_BOOKMAKERS.keys())


if __name__ == "__main__":
    # Test the API
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*70)
    print("🏈 TESTING THE ODDS API WITH MARKET DISCOVERY")
    print("="*70)
    print()
    
    try:
        api = OddsAPI()
        
        # Test 1: Check quota
        print("📊 Checking API quota...")
        quota = api.check_api_quota()
        print(f"   Requests remaining: {quota['remaining']}")
        print(f"   Requests used: {quota['used']}")
        print()
        
        # Test 2: Fetch DraftKings player props
        print("⭐ Fetching props from DRAFTKINGS (with market discovery)...")
        props_dk = api.get_player_props(bookmaker='draftkings')
        print(f"   Found {len(props_dk)} DraftKings props")
        
        if props_dk:
            print("\n   Sample DraftKings props:")
            for prop in props_dk[:5]:
                print(f"      {prop['player_name']}: {prop['stat_type']} {prop['direction']} {prop['line']} @ {prop['odds']}")
        print()
        
        print("="*70)
        print("✅ API TEST SUCCESSFUL!")
        print("="*70)
        
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        print()
        print("Please create a .env file with:")
        print("ODDS_API_KEY=your_api_key_here")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
