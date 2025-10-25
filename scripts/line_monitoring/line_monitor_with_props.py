"""
Line Movement Monitor - WITH PLAYER PROPS
Checks betting lines every hour including player props
"""
import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging
from dotenv import load_dotenv

# Load .env from project root explicitly
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LineMonitor:
    """Monitor betting lines and detect significant movements"""
    
    def __init__(self):
        self.api_key = os.getenv('ODDS_API_KEY')
        self.slack_webhook = os.getenv('SLACK_WEBHOOK')
        self.base_url = "https://api.the-odds-api.com/v4"
        
        # Debug output
        if self.api_key:
            logger.info(f"API Key loaded: {self.api_key[:10]}...")
        else:
            logger.error(f"API Key NOT found! Checked .env at: {env_path}")
            logger.error(f".env exists: {env_path.exists()}")
        
        # Paths
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "lines"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_lines_file = self.data_dir / "current_lines.json"
        self.current_props_file = self.data_dir / "current_player_props.json"
        self.history_file = self.data_dir / "line_movements_log.csv"
        
        # Alert thresholds
        self.SIGNIFICANT_MOVEMENT = 2.0  # points for game lines
        self.PROP_MOVEMENT = 5.0  # yards/points for player props (more volatile)
        
        # Player prop markets to track
        self.PLAYER_MARKETS = [
            'player_pass_tds',
            'player_pass_yds',
            'player_rush_yds',
            'player_receptions',
            'player_reception_yds',
            'player_anytime_td'
        ]
        
    def fetch_current_lines(self) -> Optional[Dict]:
        """Fetch current NFL game lines from API"""
        
        if not self.api_key:
            logger.error("ODDS_API_KEY not configured in .env")
            return None
        
        try:
            # Get NFL odds
            url = f"{self.base_url}/sports/americanfootball_nfl/odds"
            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': 'spreads,totals,h2h',
                'oddsFormat': 'american',
                'dateFormat': 'iso'
            }
            
            logger.info("Fetching current game lines from API...")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Fetched game lines for {len(data)} games")
            
            return {
                'timestamp': datetime.now().isoformat(),
                'games': data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching game lines: {e}")
            return None
    
    def fetch_player_props(self) -> Optional[Dict]:
        """Fetch current NFL player props from API"""
        
        if not self.api_key:
            logger.error("ODDS_API_KEY not configured in .env")
            return None
        
        try:
            # First get list of events
            events_url = f"{self.base_url}/sports/americanfootball_nfl/events"
            params = {
                'apiKey': self.api_key,
                'dateFormat': 'iso'
            }
            
            logger.info("Fetching NFL events...")
            response = requests.get(events_url, params=params, timeout=10)
            response.raise_for_status()
            events = response.json()
            
            logger.info(f"Found {len(events)} NFL events")
            
            # Now fetch player props for each event
            all_props = []
            
            for event in events[:10]:  # Limit to 10 games to avoid API limits
                event_id = event['id']
                
                # Fetch player props for this game
                props_url = f"{self.base_url}/sports/americanfootball_nfl/events/{event_id}/odds"
                props_params = {
                    'apiKey': self.api_key,
                    'regions': 'us',
                    'markets': ','.join(self.PLAYER_MARKETS),
                    'oddsFormat': 'american',
                    'dateFormat': 'iso'
                }
                
                logger.info(f"  Fetching props for: {event['away_team']} @ {event['home_team']}")
                
                try:
                    props_response = requests.get(props_url, params=props_params, timeout=10)
                    props_response.raise_for_status()
                    props_data = props_response.json()
                    
                    if props_data:
                        all_props.append({
                            'event_id': event_id,
                            'game': f"{event['away_team']} @ {event['home_team']}",
                            'commence_time': event['commence_time'],
                            'props': props_data
                        })
                        
                        # Count props
                        prop_count = 0
                        for bookmaker in props_data.get('bookmakers', []):
                            prop_count += len(bookmaker.get('markets', []))
                        
                        logger.info(f"    Found {prop_count} prop markets")
                        
                except Exception as e:
                    logger.warning(f"    Failed to fetch props for {event_id}: {e}")
                    continue
                
                # Small delay to avoid rate limiting
                time.sleep(0.5)
            
            logger.info(f"Fetched player props for {len(all_props)} games")
            
            return {
                'timestamp': datetime.now().isoformat(),
                'games': all_props
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            
            # Check if error is about API tier
            if '402' in str(e) or 'payment' in str(e).lower():
                logger.error("=" * 60)
                logger.error("PLAYER PROPS REQUIRE PAID API TIER!")
                logger.error("Your current tier does not include player props.")
                logger.error("Upgrade at: https://the-odds-api.com/account")
                logger.error("=" * 60)
            
            return None
        except Exception as e:
            logger.error(f"Error fetching player props: {e}")
            return None
    
    def load_previous_lines(self) -> Optional[Dict]:
        """Load previously saved game lines"""
        if not self.current_lines_file.exists():
            return None
        
        try:
            with open(self.current_lines_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading previous lines: {e}")
            return None
    
    def load_previous_props(self) -> Optional[Dict]:
        """Load previously saved player props"""
        if not self.current_props_file.exists():
            return None
        
        try:
            with open(self.current_props_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading previous props: {e}")
            return None
    
    def save_current_lines(self, lines: Dict):
        """Save current game lines for next comparison"""
        try:
            with open(self.current_lines_file, 'w') as f:
                json.dump(lines, f, indent=2)
            logger.info("Saved current game lines")
        except Exception as e:
            logger.error(f"Error saving game lines: {e}")
    
    def save_current_props(self, props: Dict):
        """Save current player props for next comparison"""
        try:
            with open(self.current_props_file, 'w') as f:
                json.dump(props, f, indent=2)
            logger.info("Saved current player props")
        except Exception as e:
            logger.error(f"Error saving player props: {e}")
    
    def detect_prop_movements(self, previous: Dict, current: Dict) -> List[Dict]:
        """Detect significant player prop movements"""
        movements = []
        
        # Create lookup for previous props
        prev_games = {game['event_id']: game for game in previous.get('games', [])}
        
        for curr_game in current.get('games', []):
            event_id = curr_game['event_id']
            
            # Skip if no previous data
            if event_id not in prev_games:
                continue
            
            prev_game = prev_games[event_id]
            
            # Compare props
            for curr_bookmaker in curr_game.get('props', {}).get('bookmakers', []):
                # Find matching previous bookmaker
                prev_bookmaker = next(
                    (b for b in prev_game.get('props', {}).get('bookmakers', [])
                     if b['key'] == curr_bookmaker['key']),
                    None
                )
                
                if not prev_bookmaker:
                    continue
                
                # Check each market
                for curr_market in curr_bookmaker.get('markets', []):
                    prev_market = next(
                        (m for m in prev_bookmaker.get('markets', [])
                         if m['key'] == curr_market['key']),
                        None
                    )
                    
                    if not prev_market:
                        continue
                    
                    # Detect movements in player props
                    prop_movements = self._compare_player_prop(
                        curr_game['game'],
                        curr_bookmaker['key'],
                        prev_market,
                        curr_market
                    )
                    
                    movements.extend(prop_movements)
        
        return movements
    
    def _compare_player_prop(self, game: str, bookmaker: str,
                            prev_market: Dict, curr_market: Dict) -> List[Dict]:
        """Compare player prop market for movements"""
        movements = []
        market_type = curr_market['key']
        
        for curr_outcome in curr_market.get('outcomes', []):
            # Find matching previous outcome
            prev_outcome = next(
                (o for o in prev_market.get('outcomes', [])
                 if o.get('description') == curr_outcome.get('description') and
                    o.get('name') == curr_outcome.get('name')),
                None
            )
            
            if not prev_outcome:
                continue
            
            # Check for movement
            prev_line = prev_outcome.get('point')
            curr_line = curr_outcome.get('point')
            
            if prev_line is None or curr_line is None:
                continue
            
            movement_abs = abs(curr_line - prev_line)
            
            # Use different threshold for props (they're more volatile)
            if movement_abs >= self.PROP_MOVEMENT:
                movements.append({
                    'type': 'player_prop',
                    'game': game,
                    'bookmaker': bookmaker,
                    'market': market_type,
                    'player': curr_outcome.get('description', 'Unknown'),
                    'prop_type': self._format_prop_type(market_type),
                    'direction': curr_outcome.get('name'),  # Over/Under
                    'previous_line': prev_line,
                    'current_line': curr_line,
                    'movement': curr_line - prev_line,
                    'movement_abs': movement_abs,
                    'timestamp': datetime.now().isoformat()
                })
        
        return movements
    
    def _format_prop_type(self, market_key: str) -> str:
        """Format market key into readable prop type"""
        mappings = {
            'player_pass_tds': 'Pass TDs',
            'player_pass_yds': 'Pass Yds',
            'player_rush_yds': 'Rush Yds',
            'player_receptions': 'Receptions',
            'player_reception_yds': 'Rec Yds',
            'player_anytime_td': 'Anytime TD'
        }
        return mappings.get(market_key, market_key)
    
    def detect_movements(self, previous: Dict, current: Dict) -> List[Dict]:
        """Detect significant game line movements"""
        movements = []
        
        # Create lookup for previous lines
        prev_games = {game['id']: game for game in previous.get('games', [])}
        
        for curr_game in current.get('games', []):
            game_id = curr_game['id']
            
            # Skip if no previous data
            if game_id not in prev_games:
                continue
            
            prev_game = prev_games[game_id]
            
            # Compare lines from each bookmaker
            for curr_bookmaker in curr_game.get('bookmakers', []):
                # Find matching previous bookmaker
                prev_bookmaker = next(
                    (b for b in prev_game.get('bookmakers', []) 
                     if b['key'] == curr_bookmaker['key']),
                    None
                )
                
                if not prev_bookmaker:
                    continue
                
                # Check each market (spreads, totals, moneyline)
                for curr_market in curr_bookmaker.get('markets', []):
                    prev_market = next(
                        (m for m in prev_bookmaker.get('markets', []) 
                         if m['key'] == curr_market['key']),
                        None
                    )
                    
                    if not prev_market:
                        continue
                    
                    # Detect movements in this market
                    market_movements = self._compare_market(
                        curr_game, curr_bookmaker['key'], 
                        prev_market, curr_market
                    )
                    
                    movements.extend(market_movements)
        
        return movements
    
    def _compare_market(self, game: Dict, bookmaker: str, 
                       prev_market: Dict, curr_market: Dict) -> List[Dict]:
        """Compare specific market for movements"""
        movements = []
        market_type = curr_market['key']
        
        for curr_outcome in curr_market.get('outcomes', []):
            # Find matching previous outcome
            prev_outcome = next(
                (o for o in prev_market.get('outcomes', []) 
                 if o['name'] == curr_outcome['name']),
                None
            )
            
            if not prev_outcome:
                continue
            
            # Calculate movement based on market type
            if market_type == 'spreads':
                movement = self._check_spread_movement(
                    game, bookmaker, prev_outcome, curr_outcome
                )
            elif market_type == 'totals':
                movement = self._check_total_movement(
                    game, bookmaker, prev_outcome, curr_outcome
                )
            else:
                continue  # Skip h2h for now
            
            if movement:
                movements.append(movement)
        
        return movements
    
    def _check_spread_movement(self, game: Dict, bookmaker: str,
                               prev: Dict, curr: Dict) -> Optional[Dict]:
        """Check for significant spread movement"""
        
        prev_line = prev.get('point', 0)
        curr_line = curr.get('point', 0)
        
        movement = abs(curr_line - prev_line)
        
        if movement >= self.SIGNIFICANT_MOVEMENT:
            return {
                'type': 'spread',
                'game': f"{game['away_team']} @ {game['home_team']}",
                'bookmaker': bookmaker,
                'team': curr['name'],
                'previous_line': prev_line,
                'current_line': curr_line,
                'movement': curr_line - prev_line,
                'movement_abs': movement,
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def _check_total_movement(self, game: Dict, bookmaker: str,
                             prev: Dict, curr: Dict) -> Optional[Dict]:
        """Check for significant total movement"""
        
        prev_line = prev.get('point', 0)
        curr_line = curr.get('point', 0)
        
        movement = abs(curr_line - prev_line)
        
        if movement >= self.SIGNIFICANT_MOVEMENT:
            return {
                'type': 'total',
                'game': f"{game['away_team']} @ {game['home_team']}",
                'bookmaker': bookmaker,
                'direction': curr['name'],  # Over or Under
                'previous_line': prev_line,
                'current_line': curr_line,
                'movement': curr_line - prev_line,
                'movement_abs': movement,
                'timestamp': datetime.now().isoformat()
            }
        
        return None
    
    def send_alert(self, movements: List[Dict]):
        """Send Slack alert for line movements"""
        
        if not movements:
            return
        
        if not self.slack_webhook:
            logger.warning("SLACK_WEBHOOK not configured - cannot send alerts")
            logger.info(f"Would have sent {len(movements)} alerts")
            return
        
        # Build message
        message = self._build_alert_message(movements)
        
        try:
            response = requests.post(
                self.slack_webhook,
                json={'text': message},
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Sent alert for {len(movements)} line movements")
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    def _build_alert_message(self, movements: List[Dict]) -> str:
        """Build formatted alert message"""
        
        lines = ["🚨 *LINE MOVEMENT ALERT*\n"]
        
        for m in movements[:10]:  # Limit to 10 per alert
            if m['type'] == 'player_prop':
                direction = "📈" if m['movement'] > 0 else "📉"
                lines.append(
                    f"{direction} *{m['player']}* - {m['prop_type']}\n"
                    f"   {m['game']}\n"
                    f"   Line: {m['previous_line']:.1f} → {m['current_line']:.1f} "
                    f"({m['movement']:+.1f})\n"
                    f"   Book: {m['bookmaker']}\n"
                )
            
            elif m['type'] == 'spread':
                direction = "📈" if m['movement'] > 0 else "📉"
                lines.append(
                    f"{direction} *{m['game']}*\n"
                    f"   {m['team']}: {m['previous_line']:+.1f} → {m['current_line']:+.1f} "
                    f"({m['movement']:+.1f})\n"
                    f"   Book: {m['bookmaker']}\n"
                )
            
            elif m['type'] == 'total':
                direction = "📈" if m['movement'] > 0 else "📉"
                lines.append(
                    f"{direction} *{m['game']}*\n"
                    f"   Total: {m['previous_line']:.1f} → {m['current_line']:.1f} "
                    f"({m['movement']:+.1f})\n"
                    f"   Book: {m['bookmaker']}\n"
                )
        
        if len(movements) > 10:
            lines.append(f"\n_...and {len(movements) - 10} more movements_")
        
        return "\n".join(lines)
    
    def log_movements(self, movements: List[Dict]):
        """Log movements to CSV for historical analysis"""
        
        if not movements:
            return
        
        try:
            import csv
            
            file_exists = self.history_file.exists()
            
            with open(self.history_file, 'a', newline='') as f:
                fieldnames = [
                    'timestamp', 'type', 'game', 'bookmaker', 
                    'team_or_player', 'prop_type', 'previous_line', 'current_line', 
                    'movement', 'movement_abs'
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                for m in movements:
                    # Flatten for CSV
                    row = {
                        'timestamp': m['timestamp'],
                        'type': m['type'],
                        'game': m['game'],
                        'bookmaker': m['bookmaker'],
                        'team_or_player': m.get('team') or m.get('player', ''),
                        'prop_type': m.get('prop_type', m.get('direction', '')),
                        'previous_line': m['previous_line'],
                        'current_line': m['current_line'],
                        'movement': m['movement'],
                        'movement_abs': m['movement_abs']
                    }
                    writer.writerow(row)
            
            logger.info(f"Logged {len(movements)} movements to CSV")
            
        except Exception as e:
            logger.error(f"Error logging movements: {e}")
    
    def run_check(self):
        """Run a single check cycle"""
        
        logger.info("=" * 60)
        logger.info("Running line movement check")
        logger.info("=" * 60)
        
        all_movements = []
        
        # 1. Check game lines
        logger.info("Checking game lines...")
        current_lines = self.fetch_current_lines()
        
        if current_lines:
            previous_lines = self.load_previous_lines()
            
            if previous_lines:
                movements = self.detect_movements(previous_lines, current_lines)
                if movements:
                    logger.info(f"Detected {len(movements)} game line movements")
                    all_movements.extend(movements)
            else:
                logger.info("No previous game lines found - first run")
            
            self.save_current_lines(current_lines)
        else:
            logger.error("Failed to fetch game lines")
        
        # 2. Check player props
        logger.info("Checking player props...")
        current_props = self.fetch_player_props()
        
        if current_props:
            previous_props = self.load_previous_props()
            
            if previous_props:
                prop_movements = self.detect_prop_movements(previous_props, current_props)
                if prop_movements:
                    logger.info(f"Detected {len(prop_movements)} player prop movements")
                    all_movements.extend(prop_movements)
            else:
                logger.info("No previous player props found - first run")
            
            self.save_current_props(current_props)
        else:
            logger.warning("Failed to fetch player props (may require paid tier)")
        
        # Send alerts and log all movements
        if all_movements:
            logger.info(f"Total movements detected: {len(all_movements)}")
            self.send_alert(all_movements)
            self.log_movements(all_movements)
        else:
            logger.info("No significant movements detected")
        
        logger.info("Check complete")
    
    def run_continuously(self, interval_minutes: int = 60):
        """Run checks continuously"""
        
        logger.info("=" * 60)
        logger.info("LINE MOVEMENT MONITOR - STARTING")
        logger.info("=" * 60)
        logger.info(f"Check interval: {interval_minutes} minutes")
        logger.info(f"Game line threshold: {self.SIGNIFICANT_MOVEMENT} points")
        logger.info(f"Player prop threshold: {self.PROP_MOVEMENT} yards/points")
        logger.info(f"API configured: {'✅' if self.api_key else '❌'}")
        logger.info(f"Slack alerts: {'✅' if self.slack_webhook else '❌'}")
        logger.info("=" * 60)
        
        if not self.api_key:
            logger.error("Cannot run - ODDS_API_KEY not configured")
            return
        
        while True:
            try:
                self.run_check()
                
                # Wait for next check
                logger.info(f"Next check in {interval_minutes} minutes...")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                logger.info("Waiting 5 minutes before retry...")
                time.sleep(300)

if __name__ == '__main__':
    monitor = LineMonitor()
    
    # Run once for testing
    monitor.run_check()
    
    # Or run continuously
    # monitor.run_continuously(interval_minutes=60)
