"""
Line Movement Monitor - With Timestamped Historical Files
Saves both current state + timestamped snapshots for historical tracking
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
        
        # Paths
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "lines"
        self.snapshots_dir = self.data_dir / "snapshots"  # NEW: Historical snapshots
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Current state files (for comparison)
        self.current_lines_file = self.data_dir / "current_lines.json"
        self.current_props_file = self.data_dir / "current_player_props.json"
        
        # Log file
        self.history_file = self.data_dir / "line_movements_log.csv"
        
        # Alert thresholds
        self.SIGNIFICANT_MOVEMENT = 2.0  # points for game lines
        self.PROP_MOVEMENT_YARDS = 5.0  # yards for passing/rushing/receiving
        self.PROP_MOVEMENT_TDS = 0.5  # TDs (any movement)
        self.PROP_MOVEMENT_COUNT = 1.0  # rushes/receptions (any movement)
        
        # YOUR 8 SPECIFIC PLAYER PROP MARKETS
        self.PLAYER_MARKETS = [
            'player_pass_yds',        # 1. Passing yards
            'player_pass_tds',        # 2. Passing TDs
            'player_rush_yds',        # 3. Rushing yards
            'player_rush_tds',        # 4. Rushing TDs
            'player_rush_attempts',   # 5. Rushes
            'player_reception_yds',   # 6. Receiving yards
            'player_reception_tds',   # 7. Receiving TDs
            'player_receptions'       # 8. Receptions
        ]
        
        logger.info(f"Tracking {len(self.PLAYER_MARKETS)} player prop types:")
        for market in self.PLAYER_MARKETS:
            logger.info(f"  - {self._format_prop_type(market)}")
    
    def _get_timestamp_str(self) -> str:
        """Get formatted timestamp for filenames"""
        return datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    def save_current_lines(self, lines: Dict):
        """Save current game lines (for comparison + as timestamped snapshot)"""
        try:
            # 1. Save as current (for next comparison)
            with open(self.current_lines_file, 'w') as f:
                json.dump(lines, f, indent=2)
            
            # 2. Save timestamped snapshot
            timestamp = self._get_timestamp_str()
            snapshot_file = self.snapshots_dir / f"game_lines_{timestamp}.json"
            with open(snapshot_file, 'w') as f:
                json.dump(lines, f, indent=2)
            
            logger.info(f"💾 Saved game lines: {snapshot_file.name}")
            
        except Exception as e:
            logger.error(f"Error saving game lines: {e}")
    
    def save_current_props(self, props: Dict):
        """Save current player props (for comparison + as timestamped snapshot)"""
        try:
            # 1. Save as current (for next comparison)
            with open(self.current_props_file, 'w') as f:
                json.dump(props, f, indent=2)
            
            # 2. Save timestamped snapshot
            timestamp = self._get_timestamp_str()
            snapshot_file = self.snapshots_dir / f"player_props_{timestamp}.json"
            with open(snapshot_file, 'w') as f:
                json.dump(props, f, indent=2)
            
            logger.info(f"💾 Saved player props: {snapshot_file.name}")
            
        except Exception as e:
            logger.error(f"Error saving player props: {e}")
    
    def cleanup_old_snapshots(self, days_to_keep: int = 7):
        """Delete snapshot files older than specified days"""
        try:
            import time
            from datetime import timedelta
            
            cutoff_time = time.time() - (days_to_keep * 86400)  # 86400 = seconds in a day
            deleted_count = 0
            
            for file in self.snapshots_dir.glob("*.json"):
                if file.stat().st_mtime < cutoff_time:
                    file.unlink()
                    deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"🗑️  Cleaned up {deleted_count} snapshots older than {days_to_keep} days")
                
        except Exception as e:
            logger.error(f"Error cleaning up snapshots: {e}")
    
    def list_snapshots(self) -> Dict[str, List[str]]:
        """List all available snapshots"""
        game_lines = sorted([f.name for f in self.snapshots_dir.glob("game_lines_*.json")])
        player_props = sorted([f.name for f in self.snapshots_dir.glob("player_props_*.json")])
        
        return {
            'game_lines': game_lines,
            'player_props': player_props,
            'total': len(game_lines) + len(player_props)
        }

    def fetch_current_lines(self) -> Optional[Dict]:
        """Fetch current NFL game lines from API"""
        
        if not self.api_key:
            logger.error("ODDS_API_KEY not configured in .env")
            return None
        
        try:
            url = f"{self.base_url}/sports/americanfootball_nfl/odds"
            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': 'spreads,totals,h2h',
                'oddsFormat': 'american',
                'dateFormat': 'iso'
            }
            
            logger.info("Fetching current game lines...")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Fetched game lines for {len(data)} games")
            
            return {
                'timestamp': datetime.now().isoformat(),
                'games': data
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching game lines: {e}")
            return None
    
    def fetch_player_props(self) -> Optional[Dict]:
        """Fetch current NFL player props from API"""
        
        if not self.api_key:
            logger.error("ODDS_API_KEY not configured")
            return None
        
        try:
            # Get list of events
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
            
            # Fetch player props for each event
            all_props = []
            total_props_count = 0
            
            for event in events[:15]:  # Limit to 15 games
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
                
                logger.info(f"  📊 {event['away_team']} @ {event['home_team']}")
                
                try:
                    props_response = requests.get(props_url, params=props_params, timeout=10)
                    props_response.raise_for_status()
                    props_data = props_response.json()
                    
                    if props_data:
                        # Count props by type
                        prop_counts = {}
                        for bookmaker in props_data.get('bookmakers', []):
                            for market in bookmaker.get('markets', []):
                                market_type = self._format_prop_type(market['key'])
                                prop_counts[market_type] = prop_counts.get(market_type, 0) + len(market.get('outcomes', []))
                        
                        if prop_counts:
                            counts_str = ', '.join([f"{k}: {v}" for k, v in prop_counts.items()])
                            logger.info(f"     ✅ {counts_str}")
                            total_props_count += sum(prop_counts.values())
                        
                        all_props.append({
                            'event_id': event_id,
                            'game': f"{event['away_team']} @ {event['home_team']}",
                            'commence_time': event['commence_time'],
                            'props': props_data
                        })
                        
                except Exception as e:
                    logger.warning(f"     ❌ Failed: {e}")
                    continue
                
                # Small delay to avoid rate limiting
                time.sleep(0.3)
            
            logger.info(f"✅ Fetched {total_props_count} total player props from {len(all_props)} games")
            
            return {
                'timestamp': datetime.now().isoformat(),
                'games': all_props
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching player props: {e}")
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
    
    def detect_prop_movements(self, previous: Dict, current: Dict) -> List[Dict]:
        """Detect significant player prop movements"""
        movements = []
        
        prev_games = {game['event_id']: game for game in previous.get('games', [])}
        
        for curr_game in current.get('games', []):
            event_id = curr_game['event_id']
            
            if event_id not in prev_games:
                continue
            
            prev_game = prev_games[event_id]
            
            # Compare props
            for curr_bookmaker in curr_game.get('props', {}).get('bookmakers', []):
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
                    
                    # Detect movements
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
        
        # Determine threshold based on prop type
        if 'yds' in market_type or 'yards' in market_type:
            threshold = self.PROP_MOVEMENT_YARDS
        elif 'tds' in market_type or 'touchdowns' in market_type:
            threshold = self.PROP_MOVEMENT_TDS
        else:  # receptions, attempts
            threshold = self.PROP_MOVEMENT_COUNT
        
        for curr_outcome in curr_market.get('outcomes', []):
            prev_outcome = next(
                (o for o in prev_market.get('outcomes', [])
                 if o.get('description') == curr_outcome.get('description') and
                    o.get('name') == curr_outcome.get('name')),
                None
            )
            
            if not prev_outcome:
                continue
            
            prev_line = prev_outcome.get('point')
            curr_line = curr_outcome.get('point')
            
            if prev_line is None or curr_line is None:
                continue
            
            movement_abs = abs(curr_line - prev_line)
            
            if movement_abs >= threshold:
                movements.append({
                    'type': 'player_prop',
                    'game': game,
                    'bookmaker': bookmaker,
                    'market': market_type,
                    'player': curr_outcome.get('description', 'Unknown'),
                    'prop_type': self._format_prop_type(market_type),
                    'direction': curr_outcome.get('name'),
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
            'player_pass_yds': 'Pass Yds',
            'player_pass_tds': 'Pass TDs',
            'player_rush_yds': 'Rush Yds',
            'player_rush_tds': 'Rush TDs',
            'player_rush_attempts': 'Rushes',
            'player_reception_yds': 'Rec Yds',
            'player_reception_tds': 'Rec TDs',
            'player_receptions': 'Receptions'
        }
        return mappings.get(market_key, market_key)
    
    def detect_movements(self, previous: Dict, current: Dict) -> List[Dict]:
        """Detect significant game line movements"""
        movements = []
        
        prev_games = {game['id']: game for game in previous.get('games', [])}
        
        for curr_game in current.get('games', []):
            game_id = curr_game['id']
            
            if game_id not in prev_games:
                continue
            
            prev_game = prev_games[game_id]
            
            for curr_bookmaker in curr_game.get('bookmakers', []):
                prev_bookmaker = next(
                    (b for b in prev_game.get('bookmakers', []) 
                     if b['key'] == curr_bookmaker['key']),
                    None
                )
                
                if not prev_bookmaker:
                    continue
                
                for curr_market in curr_bookmaker.get('markets', []):
                    prev_market = next(
                        (m for m in prev_bookmaker.get('markets', []) 
                         if m['key'] == curr_market['key']),
                        None
                    )
                    
                    if not prev_market:
                        continue
                    
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
            prev_outcome = next(
                (o for o in prev_market.get('outcomes', []) 
                 if o['name'] == curr_outcome['name']),
                None
            )
            
            if not prev_outcome:
                continue
            
            if market_type == 'spreads':
                movement = self._check_spread_movement(
                    game, bookmaker, prev_outcome, curr_outcome
                )
            elif market_type == 'totals':
                movement = self._check_total_movement(
                    game, bookmaker, prev_outcome, curr_outcome
                )
            else:
                continue
            
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
                'direction': curr['name'],
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
            logger.warning("⚠️  SLACK_WEBHOOK not configured - printing alerts instead")
            self._print_movements(movements)
            return
        
        message = self._build_alert_message(movements)
        
        try:
            response = requests.post(
                self.slack_webhook,
                json={'text': message},
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"✅ Sent alert for {len(movements)} movements to Slack")
        except Exception as e:
            logger.error(f"❌ Failed to send Slack alert: {e}")
            self._print_movements(movements)
    
    def _print_movements(self, movements: List[Dict]):
        """Print movements to console"""
        logger.info("=" * 70)
        logger.info("🚨 LINE MOVEMENTS DETECTED")
        logger.info("=" * 70)
        
        for m in movements:
            if m['type'] == 'player_prop':
                direction = "📈" if m['movement'] > 0 else "📉"
                logger.info(
                    f"{direction} {m['player']} - {m['prop_type']}\n"
                    f"   {m['game']}\n"
                    f"   {m['previous_line']:.1f} → {m['current_line']:.1f} ({m['movement']:+.1f})\n"
                    f"   {m['bookmaker']}"
                )
            elif m['type'] == 'spread':
                direction = "📈" if m['movement'] > 0 else "📉"
                logger.info(
                    f"{direction} {m['game']} - Spread\n"
                    f"   {m['team']}: {m['previous_line']:+.1f} → {m['current_line']:+.1f} ({m['movement']:+.1f})\n"
                    f"   {m['bookmaker']}"
                )
            elif m['type'] == 'total':
                direction = "📈" if m['movement'] > 0 else "📉"
                logger.info(
                    f"{direction} {m['game']} - Total\n"
                    f"   {m['previous_line']:.1f} → {m['current_line']:.1f} ({m['movement']:+.1f})\n"
                    f"   {m['bookmaker']}"
                )
        
        logger.info("=" * 70)
    
    def _build_alert_message(self, movements: List[Dict]) -> str:
        """Build formatted alert message"""
        
        lines = ["🚨 *LINE MOVEMENT ALERT*\n"]
        
        # Group by type
        props = [m for m in movements if m['type'] == 'player_prop']
        games = [m for m in movements if m['type'] in ['spread', 'total']]
        
        if props:
            lines.append("*Player Props:*")
            for m in props[:15]:
                direction = "📈" if m['movement'] > 0 else "📉"
                lines.append(
                    f"{direction} *{m['player']}* - {m['prop_type']}\n"
                    f"   {m['game']}\n"
                    f"   {m['previous_line']:.1f} → {m['current_line']:.1f} ({m['movement']:+.1f})\n"
                    f"   {m['bookmaker']}\n"
                )
        
        if games:
            lines.append("\n*Game Lines:*")
            for m in games[:10]:
                direction = "📈" if m['movement'] > 0 else "📉"
                if m['type'] == 'spread':
                    lines.append(
                        f"{direction} *{m['game']}* - Spread\n"
                        f"   {m['team']}: {m['previous_line']:+.1f} → {m['current_line']:+.1f} ({m['movement']:+.1f})\n"
                        f"   {m['bookmaker']}\n"
                    )
                else:
                    lines.append(
                        f"{direction} *{m['game']}* - Total\n"
                        f"   {m['previous_line']:.1f} → {m['current_line']:.1f} ({m['movement']:+.1f})\n"
                        f"   {m['bookmaker']}\n"
                    )
        
        total_shown = min(len(props), 15) + min(len(games), 10)
        if len(movements) > total_shown:
            lines.append(f"\n_...and {len(movements) - total_shown} more movements_")
        
        return "\n".join(lines)
    
    def log_movements(self, movements: List[Dict]):
        """Log movements to CSV"""
        
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
            
            logger.info(f"💾 Logged {len(movements)} movements to CSV")
            
        except Exception as e:
            logger.error(f"Error logging movements: {e}")
    
    def run_check(self):
        """Run a single check cycle"""
        
        logger.info("=" * 70)
        logger.info("🔍 RUNNING LINE MOVEMENT CHECK")
        logger.info(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 70)
        
        all_movements = []
        
        # 1. Check game lines
        logger.info("\n📊 Checking game lines...")
        current_lines = self.fetch_current_lines()
        
        if current_lines:
            previous_lines = self.load_previous_lines()
            
            if previous_lines:
                movements = self.detect_movements(previous_lines, current_lines)
                if movements:
                    logger.info(f"   🚨 {len(movements)} game line movements")
                    all_movements.extend(movements)
                else:
                    logger.info(f"   ✅ No significant game line movements")
            else:
                logger.info("   📝 First run - establishing baseline")
            
            self.save_current_lines(current_lines)
        
        # 2. Check player props
        logger.info("\n🏃 Checking player props...")
        current_props = self.fetch_player_props()
        
        if current_props:
            previous_props = self.load_previous_props()
            
            if previous_props:
                prop_movements = self.detect_prop_movements(previous_props, current_props)
                if prop_movements:
                    logger.info(f"   🚨 {len(prop_movements)} player prop movements")
                    all_movements.extend(prop_movements)
                else:
                    logger.info(f"   ✅ No significant player prop movements")
            else:
                logger.info("   📝 First run - establishing baseline")
            
            self.save_current_props(current_props)
        
        # Send alerts
        logger.info("")
        if all_movements:
            logger.info(f"🎯 TOTAL: {len(all_movements)} movements detected")
            self.send_alert(all_movements)
            self.log_movements(all_movements)
        else:
            logger.info("✅ No significant movements detected")
        
        # Show snapshot count
        snapshots = self.list_snapshots()
        logger.info(f"📁 Total snapshots saved: {snapshots['total']}")
        
        # Cleanup old snapshots (keep last 7 days)
        self.cleanup_old_snapshots(days_to_keep=7)
        
        logger.info("=" * 70)
        logger.info("✅ Check complete")
        logger.info("=" * 70)
    
    def run_continuously(self, interval_minutes: int = 60):
        """Run checks continuously"""
        
        logger.info("=" * 70)
        logger.info("🚀 LINE MOVEMENT MONITOR - STARTING")
        logger.info("=" * 70)
        logger.info(f"⏱️  Check interval: {interval_minutes} minutes")
        logger.info(f"📊 Game line threshold: {self.SIGNIFICANT_MOVEMENT} points")
        logger.info(f"📈 Prop thresholds:")
        logger.info(f"   - Yards: {self.PROP_MOVEMENT_YARDS}")
        logger.info(f"   - TDs: {self.PROP_MOVEMENT_TDS}")
        logger.info(f"   - Count (rushes/rec): {self.PROP_MOVEMENT_COUNT}")
        logger.info(f"🔑 API: {'✅ Configured' if self.api_key else '❌ Not configured'}")
        logger.info(f"📱 Slack: {'✅ Configured' if self.slack_webhook else '❌ Not configured'}")
        logger.info(f"📁 Snapshots will be saved to: {self.snapshots_dir}")
        logger.info(f"🗑️  Snapshots older than 7 days will be auto-deleted")
        logger.info("=" * 70)
        
        if not self.api_key:
            logger.error("❌ Cannot run - ODDS_API_KEY not configured")
            return
        
        while True:
            try:
                self.run_check()
                
                logger.info(f"\n⏳ Next check in {interval_minutes} minutes...")
                logger.info(f"   (Press Ctrl+C to stop)\n")
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("\n🛑 Stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}", exc_info=True)
                logger.info("⏳ Waiting 5 minutes before retry...")
                time.sleep(300)

if __name__ == '__main__':
    monitor = LineMonitor()
    monitor.run_check()
