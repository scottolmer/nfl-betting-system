"""
Agent Scoring Debugger - WITH PROPER PROP OBJECT
Run: python debug_agent_scoring.py
"""

import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))
logging.basicConfig(level=logging.WARNING)

load_dotenv()

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.agents.dvoa_agent import DVOAAgent
from scripts.analysis.agents.matchup_agent import MatchupAgent
from scripts.analysis.agents.volume_agent import VolumeAgent
from scripts.analysis.agents.injury_agent import InjuryAgent
from scripts.analysis.agents.trend_agent import TrendAgent
from scripts.analysis.agents.game_script_agent import GameScriptAgent
from scripts.analysis.agents.variance_agent import VarianceAgent


class PropObject:
    """Convert dict prop to object with attributes"""
    def __init__(self, prop_dict):
        self.__dict__.update(prop_dict)


def debug_agent_scoring():
    """Debug why agents aren't scoring"""
    
    print("\n" + "="*80)
    print("🐛 AGENT SCORING DEBUGGER (WITH PROPER PROP OBJECTS)")
    print("="*80 + "\n")
    
    # Load data
    loader = NFLDataLoader(data_dir="./data")
    data = loader.load_all_data(12)
    props = data.get('props', [])
    
    if not props:
        print("❌ No properties loaded!")
        return
    
    print(f"✅ Loaded {len(props)} properties\n")
    
    # Get first property and convert to object
    first_prop_dict = props[0]
    first_prop = PropObject(first_prop_dict)
    
    print(f"Testing with first property:")
    print(f"  Player: {first_prop.player_name}")
    print(f"  Stat: {first_prop.stat_type}")
    print(f"  Line: {first_prop.line}")
    print(f"  Team: {first_prop.team} vs {first_prop.opponent}\n")
    
    # Test each agent
    agents = {
        'DVOA': DVOAAgent(),
        'Matchup': MatchupAgent(),
        'Volume': VolumeAgent(),
        'Injury': InjuryAgent(),
        'Trend': TrendAgent(),
        'GameScript': GameScriptAgent(),
        'Variance': VarianceAgent(),
    }
    
    print("="*80)
    print("TESTING EACH AGENT")
    print("="*80 + "\n")
    
    successful_agents = 0
    for agent_name, agent in agents.items():
        print(f"\n{agent_name} Agent:")
        print("-" * 80)
        
        try:
            # Call analyze with proper prop object
            result = agent.analyze(first_prop, data)
            
            if isinstance(result, tuple) and len(result) >= 3:
                score, direction, rationale = result
                print(f"  ✅ Analyzed successfully!")
                print(f"  Score: {score}")
                print(f"  Direction: {direction}")
                print(f"  Rationale: {str(rationale)[:100]}")
                successful_agents += 1
            else:
                print(f"  ⚠️  Unexpected result format: {result}")
                
        except Exception as e:
            print(f"  ❌ ERROR: {type(e).__name__}: {e}")
    
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)
    print(f"\n✅ {successful_agents}/7 agents working when props are objects")
    
    if successful_agents == 7:
        print("\n🎯 PROBLEM IDENTIFIED:")
        print("   The agents WORK, but your parlay builder is passing dicts")
        print("   instead of objects. The props need to be converted.")
        print("\n💡 SOLUTION:")
        print("   1. Check parlay_builder.py")
        print("   2. Look for where it calls agent.analyze()")
        print("   3. Convert props to objects before passing to agents")
        print("   4. Use the PropObject class above as reference")
    else:
        print("\n⚠️  Some agents still have issues even with proper objects")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    debug_agent_scoring()
