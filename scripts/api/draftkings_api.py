"""
DraftKings API Client - Fetches live betting odds and player props
"""

import requests
import time
from typing import Dict, List, Optional
from datetime import datetime
import logging


class DraftKingsAPI:
    """Client for DraftKings Sportsbook API"""
    
    def __init__(self):
        self.base_url = "https://sportsbook.draftkings.com/api/odds/v1"
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
    
    def get_nfl_events(self) -> List[Dict]:
        """
        Fetch all NFL events/games
        Returns list of games with event IDs
        """
        try:
            url = f"{self.base_url}/offerings/1/events.json"
            params = {
                'category': 'Competition',
                'subcategory': 'American Football',
                'timezone': 'America/New_York'
            }
            
            self.logger.info("Fetching NFL events from DraftKings...")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse events
            events = []
            if 'events' in data:
                for event in data['events']:
                    if 'NFL' in event.get('name', ''):
                        events.append({
                            'event_id': event['id'],
                            'name': event['name'],
                            'start_time': event.get('startTime'),
                            'teams': self._parse_teams(event),
                        })
            
            self.logger.info(f"✅ Found {len(events)} NFL events")
            return events
            
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch NFL events: {e}")
            return []
    
    def get_player_props(self, event_id: str) -> List[Dict]:
        """
        Fetch player props for a specific game
        Returns list of player prop bets
        """
        try:
            url = f"{self.base_url}/offerings/1/events/{event_id}.json"
            
            self.logger.info(f"Fetching props for event {event_id}...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            props = []
            if 'markets' in data:
                for market in data['markets']:
                    # Look for player prop markets
                    if self._is_player_prop_market(market):
                        for selection in market.get('selections', []):
                            prop = self._parse_player_prop(market, selection, data)
                            if prop:
                                props.append(prop)
            
            self.logger.info(f"✅ Found {len(props)} props for event {event_id}")
            return props
            
        except Exception as e:
            self.logger.error(f"❌ Failed to fetch props for event {event_id}: {e}")
            return []
    
    def get_all_nfl_props(self, week: Optional[int] = None) -> List[Dict]:
        """
        Fetch ALL player props for all NFL games
        Optionally filter by week
        """
        all_props = []
        
        events = self.get_nfl_events()
        
        if week:
            # Filter events by week (this is approximate, needs schedule data)
            self.logger.info(f"Filtering for Week {week}...")
        
        for i, event in enumerate(events, 1):
            self.logger.info(f"Processing event {i}/{len(events)}: {event['name']}")
            
            props = self.get_player_props(event['event_id'])
            
            # Add event context to each prop
            for prop in props:
                prop['event_name'] = event['name']
                prop['start_time'] = event['start_time']
                prop['teams'] = event['teams']
            
            all_props.extend(props)
            
            # Rate limiting
            if i < len(events):
                time.sleep(1)  # Be nice to the API
        
        self.logger.info(f"✅ Total props fetched: {len(all_props)}")
        return all_props
    
    def _parse_teams(self, event: Dict) -> Dict:
        """Parse home/away teams from event"""
        teams = event.get('participants', [])
        
        home_team = None
        away_team = None
        
        for team in teams:
            if team.get('isHome'):
                home_team = team.get('name')
            else:
                away_team = team.get('name')
        
        return {
            'home': home_team,
            'away': away_team,
        }
    
    def _is_player_prop_market(self, market: Dict) -> bool:
        """Check if market is a player prop"""
        market_name = market.get('name', '').lower()
        
        player_prop_keywords = [
            'player',
            'passing yards',
            'rushing yards',
            'receiving yards',
            'receptions',
            'touchdowns',
            'completions',
            'attempts',
        ]
        
        return any(keyword in market_name for keyword in player_prop_keywords)
    
    def _parse_player_prop(self, market: Dict, selection: Dict, event_data: Dict) -> Optional[Dict]:
        """Parse a player prop from market data"""
        try:
            # Extract player name
            player_name = selection.get('name', '')
            
            # Extract stat type and line
            market_name = market.get('name', '')
            stat_type = self._extract_stat_type(market_name)
            
            # Extract line value
            line = selection.get('line')
            if line is None:
                return None
            
            # Extract odds
            odds = selection.get('price')
            
            # Determine over/under
            direction = 'OVER' if 'over' in selection.get('name', '').lower() else 'UNDER'
            
            return {
                'player_name': player_name,
                'stat_type': stat_type,
                'line': float(line),
                'direction': direction,
                'odds': odds,
                'market_id': market.get('id'),
                'selection_id': selection.get('id'),
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse prop: {e}")
            return None
    
    def _extract_stat_type(self, market_name: str) -> str:
        """Extract stat type from market name"""
        market_name = market_name.lower()
        
        stat_map = {
            'passing yards': 'Pass Yds',
            'rushing yards': 'Rush Yds',
            'receiving yards': 'Rec Yds',
            'receptions': 'Receptions',
            'pass tds': 'Pass TDs',
            'passing touchdowns': 'Pass TDs',
            'rush tds': 'Rush TDs',
            'rushing touchdowns': 'Rush TDs',
            'receiving touchdowns': 'Rec TDs',
            'completions': 'Pass Comp',
            'pass attempts': 'Pass Att',
        }
        
        for key, value in stat_map.items():
            if key in market_name:
                return value
        
        return 'Unknown'


if __name__ == "__main__":
    # Test the API
    logging.basicConfig(level=logging.INFO)
    
    api = DraftKingsAPI()
    
    print("Testing DraftKings API...")
    print("="*60)
    
    # Test 1: Get NFL events
    events = api.get_nfl_events()
    print(f"\nFound {len(events)} NFL events")
    
    if events:
        print("\nSample event:")
        print(f"  Name: {events[0]['name']}")
        print(f"  ID: {events[0]['event_id']}")
        print(f"  Teams: {events[0]['teams']}")
        
        # Test 2: Get props for first event
        print("\nFetching props for first event...")
        props = api.get_player_props(events[0]['event_id'])
        print(f"Found {len(props)} props")
        
        if props:
            print("\nSample prop:")
            print(f"  Player: {props[0]['player_name']}")
            print(f"  Stat: {props[0]['stat_type']}")
            print(f"  Line: {props[0]['line']}")
            print(f"  Direction: {props[0]['direction']}")
