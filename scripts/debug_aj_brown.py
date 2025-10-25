"""
Debug specific player - AJ Brown
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.models import PlayerProp

def normalize_player_name(name: str) -> str:
    """Normalize player name"""
    import re
    if not name:
        return name
    name = name.replace('.', '')
    name = re.sub(r'\s+', ' ', name)
    return name.strip()

def debug_aj_brown():
    print("🔍 Debugging AJ Brown Analysis")
    print("="*60)
    
    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    context = loader.load_all_data(week=7)
    
    # Create a test prop for AJ Brown
    aj_brown_prop = PlayerProp(
        player_name="AJ Brown",
        team="PHI",
        opponent="NYG",
        position="WR",
        stat_type="Rec Yds",
        line=65.5,
        week=7,
        is_home=True,
        game_total=44.5,
        spread=-3.0,
    )
    
    print(f"\n📊 Test Prop: {aj_brown_prop.player_name} {aj_brown_prop.stat_type} {aj_brown_prop.line}")
    print(f"   Team: {aj_brown_prop.team} vs {aj_brown_prop.opponent}")
    
    # Check if player is in usage data
    usage = context.get('usage', {})
    
    print(f"\n🔍 Checking usage data...")
    print(f"   Original name: '{aj_brown_prop.player_name}'")
    print(f"   Normalized: '{normalize_player_name(aj_brown_prop.player_name)}'")
    
    # Try both names
    if aj_brown_prop.player_name in usage:
        print(f"   ✅ FOUND with original name!")
        data = usage[aj_brown_prop.player_name]
        print(f"      Target share: {data.get('target_share_pct', 0):.1f}%")
        print(f"      Snap share: {data.get('snap_share_pct', 0):.1f}%")
    else:
        print(f"   ❌ NOT found with original name")
    
    normalized = normalize_player_name(aj_brown_prop.player_name)
    if normalized in usage:
        print(f"   ✅ FOUND with normalized name!")
        data = usage[normalized]
        print(f"      Target share: {data.get('target_share_pct', 0):.1f}%")
        print(f"      Snap share: {data.get('snap_share_pct', 0):.1f}%")
    else:
        print(f"   ❌ NOT found with normalized name")
    
    # Show what names ARE in the data
    print(f"\n📊 Similar names in usage data:")
    for name in usage.keys():
        if 'brown' in name.lower() and 'aj' in name.lower():
            data = usage[name]
            print(f"   '{name}'")
            print(f"      Target: {data.get('target_share_pct', 0):.1f}%")
            print(f"      Snap: {data.get('snap_share_pct', 0):.1f}%")
    
    # Now run the full analysis
    print(f"\n🧠 Running full analysis...")
    analyzer = PropAnalyzer()
    
    prop_dict = {
        'player_name': aj_brown_prop.player_name,
        'team': aj_brown_prop.team,
        'opponent': aj_brown_prop.opponent,
        'position': aj_brown_prop.position,
        'stat_type': aj_brown_prop.stat_type,
        'line': aj_brown_prop.line,
        'week': aj_brown_prop.week,
        'is_home': aj_brown_prop.is_home,
        'game_total': aj_brown_prop.game_total,
        'spread': aj_brown_prop.spread,
    }
    
    analysis = analyzer.analyze_prop(prop_dict, context)
    
    print(f"\n📊 Analysis Results:")
    print(f"   Confidence: {analysis.final_confidence}")
    print(f"   Recommendation: {analysis.recommendation}")
    print(f"\n   Agent Breakdown:")
    for agent_name, result in analysis.agent_breakdown.items():
        print(f"      {agent_name}: {result['raw_score']} (weight: {result['weight']})")
        for reason in result['rationale']:
            print(f"         • {reason}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    debug_aj_brown()
