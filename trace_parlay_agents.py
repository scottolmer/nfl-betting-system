"""
Parlay-to-Agent Trace Tool
Shows exactly which agents scored each prop in your parlays
Run: python trace_parlay_agents.py [week]
"""

import os
import sys
import json
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


def trace_parlay_agents(week=12):
    """Trace agent contributions in parlays"""
    
    print("\n" + "="*80)
    print("🔍 PARLAY AGENT TRACE TOOL (Week {})".format(week))
    print("="*80 + "\n")
    
    loader = NFLDataLoader(data_dir="./data")
    
    # Load data
    print("Loading data...")
    data = loader.load_all_data(week)
    props = data.get('props', [])
    
    if not props:
        print("❌ No properties found")
        return
    
    print(f"✅ Loaded {len(props)} properties\n")
    
    # Initialize agents
    agents = {
        'DVOA': DVOAAgent(),
        'Matchup': MatchupAgent(),
        'Volume': VolumeAgent(),
        'Injury': InjuryAgent(),
        'Trend': TrendAgent(),
        'GameScript': GameScriptAgent(),
        'Variance': VarianceAgent(),
        'Weather': WeatherAgent(),
    }
    
    print("="*80)
    print("DETAILED AGENT CONTRIBUTION BREAKDOWN")
    print("="*80 + "\n")
    
    # Score each prop and track agent contributions
    prop_agent_map = {}
    agent_usage_stats = {name: {'count': 0, 'avg_score': 0, 'scores': []} for name in agents}
    
    print(f"Scoring {len(props)} properties...\n")
    
    for i, prop in enumerate(props, 1):
        if i % 20 == 0:
            print(f"  Processed {i}/{len(props)} properties...")
        
        prop_key = f"{prop.get('player_name', '?')}_{prop.get('stat_type', '?')}_{prop.get('line', '?')}"
        prop_agent_map[prop_key] = {}
        
        for agent_name, agent in agents.items():
            try:
                score = agent.score(prop, data)
                if score is not None:
                    prop_agent_map[prop_key][agent_name] = score
                    agent_usage_stats[agent_name]['count'] += 1
                    agent_usage_stats[agent_name]['scores'].append(score)
            except Exception as e:
                pass
    
    # Calculate averages
    for agent_name, stats in agent_usage_stats.items():
        if stats['scores']:
            stats['avg_score'] = sum(stats['scores']) / len(stats['scores'])
    
    # Print agent statistics
    print("\n" + "="*80)
    print("AGENT STATISTICS")
    print("="*80)
    print(f"\n{'Agent':<15} {'Used':<10} {'Usage %':<10} {'Avg Score':<12} {'Status':<15}")
    print("-" * 80)
    
    total_prop_count = len(props)
    
    for agent_name in sorted(agents.keys()):
        stats = agent_usage_stats[agent_name]
        count = stats['count']
        usage_pct = (count / total_prop_count * 100) if total_prop_count > 0 else 0
        avg_score = stats['avg_score']
        
        if count == 0:
            status = "❌ NOT USED"
        elif usage_pct < 20:
            status = "🔶 MINIMAL"
        elif usage_pct < 50:
            status = "🟡 LIMITED"
        elif usage_pct < 80:
            status = "🟢 GOOD"
        else:
            status = "🟢 EXCELLENT"
        
        print(f"{agent_name:<15} {count:<10} {usage_pct:<10.1f}% {avg_score:<12.3f} {status:<15}")
    
    # Show sample properties with agent breakdown
    print("\n" + "="*80)
    print("SAMPLE PROPERTIES - DETAILED AGENT BREAKDOWN")
    print("="*80 + "\n")
    
    sample_props = props[:5]
    
    for i, prop in enumerate(sample_props, 1):
        prop_key = f"{prop.get('player_name', '?')}_{prop.get('stat_type', '?')}_{prop.get('line', '?')}"
        agents_used = prop_agent_map.get(prop_key, {})
        
        print(f"\n{i}. {prop.get('player_name', '?')} - {prop.get('stat_type', '?')} O/U {prop.get('line', '?')}")
        print(f"   Team: {prop.get('team', '?')} vs {prop.get('opponent', '?')}")
        print("   " + "-" * 76)
        
        if agents_used:
            for agent_name, score in sorted(agents_used.items(), key=lambda x: x[1], reverse=True):
                if score >= 0.7:
                    emoji = "✅"
                elif score >= 0.55:
                    emoji = "👍"
                elif score <= 0.45:
                    emoji = "👎"
                else:
                    emoji = "➖"
                
                print(f"   {emoji} {agent_name:15s} | Score: {score:.3f}")
        else:
            print("   ⚠️  No agents scored this property!")
        
        avg = sum(agents_used.values()) / len(agents_used) if agents_used else 0
        print(f"   {'─'*76}")
        print(f"   📊 Average: {avg:.3f} | Agents Used: {len(agents_used)}/8")
    
    # Show properties with agent coverage issues
    print("\n" + "="*80)
    print("COVERAGE ANALYSIS")
    print("="*80 + "\n")
    
    coverage_issues = []
    no_agent_props = []
    
    for prop_key, agents_used in prop_agent_map.items():
        if len(agents_used) < 3:
            coverage_issues.append((prop_key, len(agents_used)))
        if len(agents_used) == 0:
            no_agent_props.append(prop_key)
    
    print(f"Total Properties: {len(props)}")
    print(f"Properties with <3 agents: {len(coverage_issues)} ({len(coverage_issues)/len(props)*100:.1f}%)")
    print(f"Properties with NO agents: {len(no_agent_props)} ({len(no_agent_props)/len(props)*100:.1f}%)")
    
    if no_agent_props:
        print(f"\n⚠️  Properties with NO agent coverage:")
        for prop_key in no_agent_props[:5]:
            print(f"   • {prop_key}")
        if len(no_agent_props) > 5:
            print(f"   ... and {len(no_agent_props) - 5} more")
    
    if coverage_issues:
        print(f"\n🟡 Properties with LOW agent coverage (<3 agents):")
        for prop_key, agent_count in coverage_issues[:5]:
            print(f"   • {prop_key} ({agent_count} agents)")
        if len(coverage_issues) > 5:
            print(f"   ... and {len(coverage_issues) - 5} more")
    
    print("\n" + "="*80)
    print("✅ TRACE COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    week = 12
    if len(sys.argv) > 1:
        try:
            week = int(sys.argv[1])
        except:
            pass
    
    trace_parlay_agents(week)
