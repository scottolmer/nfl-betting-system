"""
Enhanced Line Monitor - Command Line Version with Confidence Scoring
Combines line movement detection with system confidence integration
"""
import sys
from pathlib import Path
import logging
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.line_monitoring.line_monitor import LineMonitor
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from dotenv import load_dotenv
from datetime import datetime

# Load environment
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedLineMonitorCLI(LineMonitor):
    """Enhanced line monitor with confidence scoring for CLI"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize analysis system
        self.data_loader = NFLDataLoader(data_dir=str(project_root / "data"))
        self.prop_analyzer = PropAnalyzer()
        self.confidence_cache = {}
        self.analyses_loaded = False
        self.all_analyses = []
    
    def get_prop_confidence(self, player_name, stat_type, team):
        """Get system confidence for a prop"""
        cache_key = f"{player_name}_{stat_type}_{team}"
        
        # Check cache
        if cache_key in self.confidence_cache:
            return self.confidence_cache[cache_key]
        
        try:
            week = int(os.environ.get('NFL_WEEK', 7))
            
            # Load data if not already loaded
            if not self.analyses_loaded:
                logger.info("   📊 Loading analysis data...")
                context = self.data_loader.load_all_data(week=week)
                self.all_analyses = self.prop_analyzer.analyze_all_props(context, min_confidence=50)
                self.analyses_loaded = True
            
            # Find matching prop
            for analysis in self.all_analyses:
                prop = analysis.prop
                if (player_name.lower() in prop.player_name.lower() and 
                    stat_type in prop.stat_type and
                    team == prop.team):
                    
                    confidence = analysis.final_confidence
                    self.confidence_cache[cache_key] = confidence
                    return confidence
            
            # Not found
            return None
            
        except Exception as e:
            logger.debug(f"Error getting confidence: {e}")
            return None
    
    def get_confidence_emoji_and_level(self, confidence):
        """Return emoji and level for confidence score"""
        if confidence >= 75:
            return "🔥", "ELITE", "█████"
        elif confidence >= 70:
            return "⭐", "HIGH", "████░"
        elif confidence >= 65:
            return "✅", "GOOD", "███░░"
        elif confidence >= 60:
            return "📊", "MODERATE", "██░░░"
        else:
            return "⚠️", "LOW", "█░░░░"
    
    def format_movement_with_confidence(self, movement):
        """Format movement alert with confidence score"""
        
        output = []
        
        if movement['type'] == 'player_prop':
            # Get confidence
            confidence = self.get_prop_confidence(
                movement['player'],
                movement['prop_type'],
                movement.get('team', '')
            )
            
            direction = "📈" if movement['movement'] > 0 else "📉"
            
            output.append(f"\n   {direction} *{movement['player']}* - {movement['prop_type']}")
            output.append(f"      Game: {movement['game']}")
            output.append(f"      Line: {movement['previous_line']:.1f} → {movement['current_line']:.1f} ({movement['movement']:+.1f})")
            output.append(f"      Sportsbook: {movement['bookmaker']}")
            
            if confidence:
                emoji, level, bar = self.get_confidence_emoji_and_level(confidence)
                output.append(f"      {emoji} System Confidence: {confidence:.0f}% [{bar}] {level}")
                
                # Add action recommendation based on confidence
                if confidence >= 75:
                    output.append(f"      🎯 RECOMMENDATION: MAX BET - Elite alignment")
                elif confidence >= 70:
                    output.append(f"      🎯 RECOMMENDATION: Standard bet - Strong alignment")
                elif confidence >= 65:
                    output.append(f"      🎯 RECOMMENDATION: Consider betting")
                elif confidence >= 60:
                    output.append(f"      ⚠️  RECOMMENDATION: Small sizing only")
                else:
                    output.append(f"      ⛔ RECOMMENDATION: PASS - Low system confidence")
        
        elif movement['type'] == 'spread':
            direction = "📈" if movement['movement'] > 0 else "📉"
            output.append(f"\n   {direction} *{movement['game']}* - SPREAD")
            output.append(f"      {movement['team']}: {movement['previous_line']:+.1f} → {movement['current_line']:+.1f} ({movement['movement']:+.1f})")
            output.append(f"      Sportsbook: {movement['bookmaker']}")
        
        elif movement['type'] == 'total':
            direction = "📈" if movement['movement'] > 0 else "📉"
            output.append(f"\n   {direction} *{movement['game']}* - TOTAL")
            output.append(f"      {movement['previous_line']:.1f} → {movement['current_line']:.1f} ({movement['movement']:+.1f})")
            output.append(f"      Sportsbook: {movement['bookmaker']}")
        
        return "\n".join(output)
    
    def run_check_enhanced(self):
        """Run a single check cycle with enhanced output"""
        
        self._print_header()
        
        all_movements = []
        
        # 1. Check game lines
        logger.info("")
        logger.info("   📊 Checking game lines...")
        current_lines = self.fetch_current_lines()
        
        if current_lines:
            previous_lines = self.load_previous_lines()
            
            if previous_lines:
                movements = self.detect_movements(previous_lines, current_lines)
                if movements:
                    logger.info(f"   🚨 {len(movements)} game line movements detected")
                    all_movements.extend(movements)
                else:
                    logger.info(f"   ✅ No significant game line movements")
            else:
                logger.info("   📝 First run - establishing baseline")
            
            self.save_current_lines(current_lines)
        
        # 2. Check player props
        logger.info("")
        logger.info("   🏃 Checking player props...")
        current_props = self.fetch_player_props()
        
        if current_props:
            previous_props = self.load_previous_props()
            
            if previous_props:
                prop_movements = self.detect_prop_movements(previous_props, current_props)
                if prop_movements:
                    logger.info(f"   🚨 {len(prop_movements)} player prop movements detected")
                    all_movements.extend(prop_movements)
                else:
                    logger.info(f"   ✅ No significant player prop movements")
            else:
                logger.info("   📝 First run - establishing baseline")
            
            self.save_current_props(current_props)
        
        # Display results
        logger.info("")
        if all_movements:
            self._print_movements_report(all_movements)
            self.send_alert(all_movements)
            self.log_movements(all_movements)
        else:
            logger.info("   ✅ No significant movements detected")
        
        # Show snapshot info
        logger.info("")
        snapshots = self.list_snapshots()
        logger.info(f"   📁 Total snapshots saved: {snapshots['total']}")
        
        # Cleanup
        self.cleanup_old_snapshots(days_to_keep=7)
        
        self._print_footer()
    
    def _print_header(self):
        """Print formatted header"""
        logger.info("")
        logger.info("╔══════════════════════════════════════════════════════════════╗")
        logger.info("║                                                              ║")
        logger.info("║        🏈 NFL LINE MOVEMENT MONITOR WITH CONFIDENCE 🏈       ║")
        logger.info("║                                                              ║")
        logger.info("╚══════════════════════════════════════════════════════════════╝")
        logger.info("")
        logger.info(f"   ⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   📅 NFL Week: {os.environ.get('NFL_WEEK', 'N/A')}")
        logger.info(f"   🔑 API: {'✅ Configured' if self.api_key else '❌ Not configured'}")
        logger.info(f"   📱 Slack: {'✅ Configured' if self.slack_webhook else '❌ Not configured'}")
    
    def _print_movements_report(self, movements):
        """Print detailed movements report"""
        
        # Separate by type
        props = [m for m in movements if m['type'] == 'player_prop']
        spreads = [m for m in movements if m['type'] == 'spread']
        totals = [m for m in movements if m['type'] == 'total']
        
        logger.info("")
        logger.info("   🎯 LINE MOVEMENTS DETECTED:")
        logger.info("   " + "─" * 58)
        
        # Player props
        if props:
            logger.info("")
            logger.info(f"   📊 PLAYER PROPS ({len(props)} movements):")
            for movement in sorted(props, key=lambda x: x.get('movement_abs', 0), reverse=True)[:15]:
                logger.info(self.format_movement_with_confidence(movement))
        
        # Spreads
        if spreads:
            logger.info("")
            logger.info(f"   📈 SPREADS ({len(spreads)} movements):")
            for movement in sorted(spreads, key=lambda x: x.get('movement_abs', 0), reverse=True)[:10]:
                logger.info(self.format_movement_with_confidence(movement))
        
        # Totals
        if totals:
            logger.info("")
            logger.info(f"   📊 TOTALS ({len(totals)} movements):")
            for movement in sorted(totals, key=lambda x: x.get('movement_abs', 0), reverse=True)[:10]:
                logger.info(self.format_movement_with_confidence(movement))
        
        # Summary
        logger.info("")
        logger.info("   " + "─" * 58)
        logger.info(f"   📊 SUMMARY: {len(movements)} total movements detected")
        
        if len(movements) > 35:
            logger.info(f"   ... and {len(movements) - 35} more (showing top 35)")
        
        # Confidence distribution
        if props:
            conf_high = sum(1 for m in props if self.get_prop_confidence(m['player'], m['prop_type'], m.get('team', '')) and 
                           self.get_prop_confidence(m['player'], m['prop_type'], m.get('team', '')) >= 70)
            logger.info("")
            logger.info(f"   💡 High Confidence Moves (70+): {conf_high}/{len(props)}")
    
    def _print_footer(self):
        """Print formatted footer"""
        logger.info("")
        logger.info("   ✅ Check complete")
        logger.info("")
    
    def run_continuously_enhanced(self, interval_minutes: int = 60):
        """Run checks continuously with enhanced output"""
        
        logger.info("")
        logger.info("╔══════════════════════════════════════════════════════════════╗")
        logger.info("║                                                              ║")
        logger.info("║        🚀 STARTING NFL LINE MOVEMENT MONITOR 🚀              ║")
        logger.info("║                                                              ║")
        logger.info("╚══════════════════════════════════════════════════════════════╝")
        logger.info("")
        logger.info("   ⚙️  CONFIGURATION:")
        logger.info(f"      • Check Interval: {interval_minutes} minutes")
        logger.info(f"      • Game Line Threshold: {self.SIGNIFICANT_MOVEMENT} points")
        logger.info(f"      • Prop Thresholds:")
        logger.info(f"        - Yards: {self.PROP_MOVEMENT_YARDS}")
        logger.info(f"        - TDs: {self.PROP_MOVEMENT_TDS}")
        logger.info(f"        - Count: {self.PROP_MOVEMENT_COUNT}")
        logger.info("")
        logger.info("   📊 ANALYSIS INTEGRATION:")
        logger.info("      • 8-Agent Confidence Scoring: ✅")
        logger.info("      • Slack Alerts: " + ('✅' if self.slack_webhook else '⚠️  (Output only)'))
        logger.info("      • Historical Tracking: ✅")
        logger.info("      • Snapshot Storage: ✅")
        logger.info("")
        logger.info("   💾 DATA LOCATIONS:")
        logger.info(f"      • Current State: {self.data_dir}")
        logger.info(f"      • Snapshots: {self.snapshots_dir}")
        logger.info(f"      • History: {self.history_file}")
        logger.info("")
        logger.info("   📌 Press Ctrl+C to stop monitoring")
        logger.info("")
        logger.info("╔══════════════════════════════════════════════════════════════╗")
        
        if not self.api_key:
            logger.error("")
            logger.error("   ❌ ERROR: ODDS_API_KEY not configured in .env")
            logger.error("   ❌ Cannot start monitoring without API access")
            return
        
        import time
        
        first_run = True
        
        while True:
            try:
                if not first_run:
                    logger.info("")
                    logger.info("")
                
                self.run_check_enhanced()
                
                first_run = False
                
                logger.info("")
                logger.info(f"   ⏳ Next check in {interval_minutes} minutes...")
                logger.info(f"   ⏰ Scheduled for: {datetime.fromtimestamp(datetime.now().timestamp() + interval_minutes * 60).strftime('%H:%M:%S')}")
                logger.info("")
                
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("")
                logger.info("   🛑 Monitoring stopped by user")
                logger.info("")
                break
            except Exception as e:
                logger.error(f"   ❌ Error in monitoring loop: {e}", exc_info=False)
                logger.info("   ⏳ Waiting 5 minutes before retry...")
                time.sleep(300)


def main():
    """Main entry point"""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description='NFL Line Movement Monitor with Confidence Scoring',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python monitor_main_enhanced.py                    # Single check
  python monitor_main_enhanced.py --continuous       # Continuous monitoring (60 min interval)
  python monitor_main_enhanced.py --interval 30      # Continuous with 30 min interval
        """
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuous monitoring'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in minutes (default: 60)'
    )
    
    parser.add_argument(
        '--week',
        type=int,
        help='Override NFL week (otherwise uses NFL_WEEK env var)'
    )
    
    args = parser.parse_args()
    
    # Override week if specified
    if args.week:
        os.environ['NFL_WEEK'] = str(args.week)
    
    # Create monitor
    monitor = EnhancedLineMonitorCLI()
    
    # Run
    if args.continuous:
        monitor.run_continuously_enhanced(interval_minutes=args.interval)
    else:
        monitor.run_check_enhanced()


if __name__ == "__main__":
    main()
