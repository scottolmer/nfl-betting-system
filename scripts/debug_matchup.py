"""
Debug Matchup Agent specifically
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.agents.matchup_agent import MatchupAgent
from scripts.analysis.models import PlayerProp

def debug_matchup():
    print("🔍 Debugging Matchup Agent for AJ Brown")
    print("="*60)
    
    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    context = loader.load_all_data(week=7)
    
    # Create test prop
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
    
    print(f"\n📊 Test Prop: {aj_brown_prop.player_name}")
    print(f"   Position: {aj_brown_prop.position}")
    print(f"   Opponent: {aj_brown_prop.opponent}")
    
    # Check alignment data
    alignment = context.get('alignment', {})
    usage = context.get('usage', {})
    
    print(f"\n🔍 Checking alignment for AJ Brown...")
    if "AJ Brown" in alignment:
        align_data = alignment["AJ Brown"]
        print(f"   ✅ Found alignment:")
        print(f"      Slot %: {align_data.get('slot_pct', 0):.1f}%")
        print(f"      Wide %: {align_data.get('wide_pct', 0):.1f}%")
    else:
        print(f"   ❌ Not found in alignment data")
    
    if "AJ Brown" in usage:
        usage_data = usage["AJ Brown"]
        print(f"   ✅ Found usage:")
        print(f"      Target share: {usage_data.get('target_share_pct', 0):.1f}%")
    
    # Check defensive data
    def_vs_receiver = context.get('defensive_vs_receiver', {})
    print(f"\n🔍 Checking NYG defensive data...")
    if "NYG" in def_vs_receiver:
        def_data = def_vs_receiver["NYG"]
        print(f"   ✅ Found NYG defense:")
        print(f"      vs WR1 DVOA: {def_data.get('vs_wr1_dvoa', 0):.1f}%")
        print(f"      vs WR2 DVOA: {def_data.get('vs_wr2_dvoa', 0):.1f}%")
        print(f"      vs WR3 DVOA: {def_data.get('vs_wr3_dvoa', 0):.1f}%")
    else:
        print(f"   ❌ NYG not found in defensive data")
        print(f"   Available teams: {list(def_vs_receiver.keys())[:10]}")
    
    # Now run the Matchup agent
    print(f"\n🧠 Running Matchup Agent...")
    matchup_agent = MatchupAgent()
    
    # Call the role classifier directly
    wr_role = matchup_agent._classify_wr_role(
        aj_brown_prop.player_name, 
        aj_brown_prop.position, 
        context
    )
    print(f"   Classified role: {wr_role}")
    
    # Run full analysis
    score, direction, rationale = matchup_agent.analyze(aj_brown_prop, context)
    
    print(f"\n📊 Matchup Agent Results:")
    print(f"   Score: {score}")
    print(f"   Direction: {direction}")
    print(f"   Rationale:")
    for reason in rationale:
        print(f"      • {reason}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    debug_matchup()
