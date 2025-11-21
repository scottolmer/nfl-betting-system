"""
Quick Agent Status Checker - FIXED for fallback data
Lightweight diagnostic to see which agents are active
Run: python quick_agent_check.py [week]
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
logging.basicConfig(level=logging.WARNING)

load_dotenv()

try:
    from scripts.analysis.data_loader import NFLDataLoader
    from scripts.analysis.agents.dvoa_agent import DVOAAgent
    from scripts.analysis.agents.matchup_agent import MatchupAgent
    from scripts.analysis.agents.volume_agent import VolumeAgent
    from scripts.analysis.agents.injury_agent import InjuryAgent
    from scripts.analysis.agents.trend_agent import TrendAgent
    from scripts.analysis.agents.game_script_agent import GameScriptAgent
    from scripts.analysis.agents.variance_agent import VarianceAgent
    from scripts.analysis.agents.weather_agent import WeatherAgent
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def quick_agent_check(week=12):
    """Quick check of agent status"""
    
    print("\n" + "="*70)
    print("⚡ QUICK AGENT STATUS CHECK (Week {})".format(week))
    print("="*70 + "\n")
    
    loader = NFLDataLoader(data_dir="./data")
    data = loader.load_all_data(week)
    
    agents = [
        ('DVOA', DVOAAgent()),
        ('Matchup', MatchupAgent()),
        ('Volume', VolumeAgent()),
        ('Injury', InjuryAgent()),
        ('Trend', TrendAgent()),
        ('GameScript', GameScriptAgent()),
        ('Variance', VarianceAgent()),
        ('Weather', WeatherAgent()),
    ]
    
    print("AGENT STATUS:")
    print("-" * 70)
    
    active_count = 0
    for name, agent in agents:
        # Check for required data - use correct keys from loader
        has_data = False
        data_source = ""
        
        if name == 'DVOA':
            # Check for transformed DVOA data (offensive/defensive)
            has_data = bool(data.get('dvoa_offensive') or data.get('dvoa_defensive'))
            data_source = "DVOA (off/def)"
        elif name == 'Matchup':
            # Check for defensive vs receiver matchup data
            has_data = bool(data.get('defensive_vs_receiver'))
            data_source = "Def vs WR DVOA"
        elif name == 'Volume':
            # Check for usage/snap count data
            has_data = bool(data.get('usage'))
            data_source = "Usage/Snap data"
        elif name == 'Injury':
            # Check for injury report content
            has_data = bool(data.get('injuries'))
            data_source = "Injury report"
        elif name == 'Trend':
            # Check for historical/trend data
            has_data = bool(data.get('trends') or data.get('historical_stats'))
            data_source = "Historical trends"
        elif name == 'GameScript':
            # Check for props (betting lines transformed to props)
            has_data = bool(data.get('props'))
            data_source = "Props/Game context"
        elif name == 'Variance':
            has_data = True  # Always available
            data_source = "Statistical"
        elif name == 'Weather':
            has_data = bool(data.get('weather'))
            data_source = "Weather data"
        
        if has_data:
            print(f"✅ {name:15s} | ACTIVE   | {data_source}")
            active_count += 1
        else:
            print(f"❌ {name:15s} | INACTIVE | Missing {data_source}")
    
    print("\n" + "-" * 70)
    print(f"SUMMARY: {active_count}/8 agents active")
    
    if active_count < 5:
        print("\n⚠️  WARNING: Few agents active!")
        print("Note: If week {} hasn't been played yet, stats may be falling back to week {}".format(week, week-1))
    elif active_count >= 7:
        print("\n✅ Good: Most agents are active")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    week = 12
    if len(sys.argv) > 1:
        try:
            week = int(sys.argv[1])
        except:
            pass
    
    quick_agent_check(week)
