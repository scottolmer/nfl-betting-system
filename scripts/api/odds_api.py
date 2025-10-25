"""
The Odds API Client - Fetches NFL player props
Documentation: https://the-odds-api.com/
"""

import requests
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging
from dotenv import load_dotenv


class OddsAPI:
    """Client for The Odds API"""
    
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
        """
        Fetch all upcoming NFL events
        Returns list of games with event IDs
        """
        try:
            url = f"{self.base_url}/sports/americanfootball_nfl/odds"
            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': 'h2h',  # Just need game info
                'oddsFormat': 'american',
            }
            
            self.logger.info("Fetching NFL events from The Odds API...")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse events
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
    
    def get_player_props(self, regions: str = 'us', markets: str = 'player_pass_tds,player_pass_yds,player_rush_yds,player_receptions,player_reception_yds') -> List[Dict]:
        """
        Fetch all player props for NFL
        
        Available markets:
        - player_pass_tds, player_pass_yds, player_pass_completions, player_pass_attempts
        - player_rush_yds, player_rush_attempts, player_rush_reception_yds
        - player_receptions, player_reception_yds
        - player_touchdowns, player_kicking_points
        """
        try:
            url = f"{self.base_url}/sports/americanfootball_nfl/odds"
            params = {
                'apiKey': self.api_key,
                'regions': regions,
                'markets': markets,
                'oddsFormat': 'american',
            }
            
            self.logger.info("Fetching NFL player props from The Odds API...")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse all props
            all_props = []
            for event in data:
                event_props = self._parse_event_props(event)
                all_props.extend(event_props)
            
            self.logger.info(f"✅ Found {len(all_props)} total props")
            self._log_remaining_requests(response)
            
            return all_props
            
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch player props: {e}")
            return []
    
    def _parse_event_props(self, event: Dict) -> List[Dict]:
        """Parse all props from a single event"""
        props = []
        
        event_id = event['id']
        home_team = event['home_team']
        away_team = event['away_team']
        commence_time = event['commence_time']
        
        # Get bookmakers data
        for bookmaker in event.get('bookmakers', []):
            bookmaker_name = bookmaker['key']
            
            # Parse each market
            for market in bookmaker.get('markets', []):
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
            # Make a minimal request to check quota
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


if __name__ == "__main__":
    # Test the API
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("🏈 TESTING THE ODDS API CONNECTION")
    print("="*60)
    print()
    
    try:
        api = OddsAPI()
        
        # Test 1: Check quota
        print("📊 Checking API quota...")
        quota = api.check_api_quota()
        print(f"   Requests remaining: {quota['remaining']}")
        print(f"   Requests used: {quota['used']}")
        print()
        
        # Test 2: Get NFL events
        print("🏈 Fetching NFL events...")
        events = api.get_nfl_events()
        print(f"   Found {len(events)} events")
        
        if events:
            print("\n   Sample event:")
            print(f"      {events[0]['away_team']} @ {events[0]['home_team']}")
            print(f"      Event ID: {events[0]['event_id']}")
        print()
        
        # Test 3: Get player props (limited markets for testing)
        print("🎯 Fetching player props (this uses 1 API request)...")
        print("   Markets: Pass Yds, Rec Yds, Rush Yds")
        
        props = api.get_player_props(
            markets='player_pass_yds,player_reception_yds,player_rush_yds'
        )
        
        print(f"   Found {len(props)} props")
        
        if props:
            print("\n   Sample props:")
            for prop in props[:3]:
                print(f"      {prop['player_name']}: {prop['stat_type']} {prop['direction']} {prop['line']}")
        
        print()
        print("="*60)
        print("✅ API TEST SUCCESSFUL!")
        print("="*60)
        
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        print()
        print("Please create a .env file with:")
        print("ODDS_API_KEY=your_api_key_here")
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
