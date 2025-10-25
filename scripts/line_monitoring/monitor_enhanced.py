"""
Enhanced Line Monitor - Integrated with Confidence Scoring

Monitors line movements and includes system confidence for each prop
"""

import sys
from pathlib import Path
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.line_monitoring.line_monitor import LineMonitor
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class EnhancedLineMonitor(LineMonitor):
    """Line monitor with confidence scoring integration"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize analysis system
        self.data_loader = NFLDataLoader(data_dir=str(project_root / "data"))
        self.prop_analyzer = PropAnalyzer()
        self.confidence_cache = {}
    
    def get_prop_confidence(self, player_name, stat_type, team):
        """Get system confidence for a prop"""
        cache_key = f"{player_name}_{stat_type}_{team}"
        
        # Check cache
        if cache_key in self.confidence_cache:
            return self.confidence_cache[cache_key]
        
        try:
            week = int(os.environ.get('NFL_WEEK', 7))
            
            # Load data if not already loaded
            if not hasattr(self, 'analyses_loaded'):
                logger.info("Loading analysis data...")
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
            logger.error(f"Error getting confidence: {e}")
            return None
    
    def format_movement_alert(self, movement):
        """Format movement alert with confidence score"""
        alert = super().format_movement_alert(movement)
        
        # Add confidence if it's a player prop
        if 'player' in movement:
            player = movement['player']
            stat_type = movement.get('market', '')
            team = movement.get('home_team', '')  # Simplified
            
            confidence = self.get_prop_confidence(player, stat_type, team)
            
            if confidence:
                # Add confidence rating
                if confidence >= 75:
                    conf_text = f"\n🔥 *SYSTEM CONFIDENCE: {confidence}* (ELITE - MAX BET)"
                elif confidence >= 70:
                    conf_text = f"\n⭐ *SYSTEM CONFIDENCE: {confidence}* (HIGH)"
                elif confidence >= 65:
                    conf_text = f"\n✅ *SYSTEM CONFIDENCE: {confidence}* (GOOD)"
                elif confidence >= 60:
                    conf_text = f"\n📊 *SYSTEM CONFIDENCE: {confidence}* (MODERATE)"
                else:
                    conf_text = f"\n⚠️ *SYSTEM CONFIDENCE: {confidence}* (LOW - PASS)"
                
                alert += conf_text
        
        return alert


def run_enhanced_monitor():
    """Run the enhanced line monitor"""
    logger.info("="*60)
    logger.info("🏈 ENHANCED LINE MONITOR WITH CONFIDENCE SCORING")
    logger.info("="*60)
    logger.info("")
    logger.info("Features:")
    logger.info("  ✅ Track game lines + player props")
    logger.info("  ✅ Detect significant movements")
    logger.info("  ✅ System confidence integration")
    logger.info("  ✅ Slack alerts with ratings")
    logger.info("")
    
    # Check if API configured
    if not os.getenv('ODDS_API_KEY'):
        logger.error("❌ ODDS_API_KEY not found in .env")
        logger.error("Please add: ODDS_API_KEY=your_key_here")
        return
    
    # Initialize monitor
    monitor = EnhancedLineMonitor()
    
    # Check initial data
    week = int(os.getenv('NFL_WEEK', 7))
    logger.info(f"📅 Monitoring Week {week}")
    logger.info("")
    
    # Start monitoring
    logger.info("🚀 Starting continuous monitoring...")
    logger.info("   Interval: 60 minutes (change in code if needed)")
    logger.info("   Press Ctrl+C to stop")
    logger.info("")
    
    try:
        monitor.run_continuously(interval_minutes=60)
    except KeyboardInterrupt:
        logger.info("\n🛑 Monitor stopped by user")
    except Exception as e:
        logger.error(f"❌ Monitor error: {e}")


if __name__ == "__main__":
    run_enhanced_monitor()
