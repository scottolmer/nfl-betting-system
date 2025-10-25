"""
Find the highest potential confidence props
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

def find_elite_props():
    print("🔍 Finding Elite Confidence Props")
    print("="*60)
    
    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    context = loader.load_all_data(week=7)
    analyzer = PropAnalyzer()
    
    print(f"📊 Analyzing all {len(context['props'])} props...")
    print(f"Looking for:")
    print(f"   • Elite volume (28%+ target share or 75%+ snap share)")
    print(f"   • Elite matchups (DVOA 30+)")
    print(f"   • Confidence 70+")
    print()
    
    all_analyses = []
    
    for prop_dict in context['props']:
        analysis = analyzer.analyze_prop(prop_dict, context)
        all_analyses.append(analysis)
    
    # Sort by confidence
    all_analyses.sort(key=lambda x: x.final_confidence, reverse=True)
    
    # Show TOP 10
    print("="*60)
    print("🏆 TOP 10 HIGHEST CONFIDENCE PROPS")
    print("="*60)
    
    for i, analysis in enumerate(all_analyses[:10], 1):
        prop = analysis.prop
        
        print(f"\n{i}. {analysis.recommendation}")
        print(f"   Player: {prop.player_name} ({prop.team} vs {prop.opponent})")
        print(f"   Bet: {prop.stat_type} {prop.direction} {prop.line}")
        print(f"   Confidence: {analysis.final_confidence}")
        
        # Show ALL agent scores
        print(f"   Agent Breakdown:")
        for agent_name, result in analysis.agent_breakdown.items():
            score = result['raw_score']
            weight = result['weight']
            rationale = result['rationale'][:2]  # First 2 reasons
            
            if score != 50 or rationale:  # Only show non-neutral agents
                print(f"      {agent_name}: {score} (×{weight})")
                for reason in rationale:
                    print(f"         • {reason}")
    
    # Find props with elite volume
    print("\n" + "="*60)
    print("🎯 ELITE VOLUME PLAYERS (not necessarily high confidence)")
    print("="*60)
    
    usage = context.get('usage', {})
    elite_volume = []
    
    for player_name, data in usage.items():
        target_share = data.get('target_share_pct', 0)
        snap_share = data.get('snap_share_pct', 0)
        
        if target_share >= 28 or snap_share >= 75:
            elite_volume.append({
                'player': player_name,
                'target_share': target_share,
                'snap_share': snap_share,
            })
    
    elite_volume.sort(key=lambda x: x['target_share'], reverse=True)
    
    for player_data in elite_volume[:15]:
        print(f"   {player_data['player']}")
        print(f"      Target: {player_data['target_share']:.1f}%")
        print(f"      Snap: {player_data['snap_share']:.1f}%")
    
    print("\n" + "="*60)
    print("✅ Analysis complete!")

if __name__ == "__main__":
    find_elite_props()
