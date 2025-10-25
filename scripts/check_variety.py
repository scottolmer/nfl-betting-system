"""
Check confidence distribution across games
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

def check_variety():
    print("🔍 Checking prop variety across games...")
    print("="*60)
    
    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    context = loader.load_all_data(week=7)
    
    analyzer = PropAnalyzer()
    all_analyses = analyzer.analyze_all_props(context, min_confidence=50)
    
    # Group by game and confidence range
    games_75_plus = {}
    games_65_to_74 = {}
    
    for analysis in all_analyses:
        game = f"{analysis.prop.team} vs {analysis.prop.opponent}"
        conf = analysis.final_confidence
        
        if conf >= 75:
            if game not in games_75_plus:
                games_75_plus[game] = []
            games_75_plus[game].append(analysis)
        elif conf >= 65:
            if game not in games_65_to_74:
                games_65_to_74[game] = []
            games_65_to_74[game].append(analysis)
    
    print("\n📊 Games with 75+ confidence props:")
    for game, props in sorted(games_75_plus.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
        print(f"   {game}: {len(props)} props")
        for prop in props[:3]:
            print(f"      • {prop.prop.player_name} {prop.prop.stat_type} {prop.final_confidence}")
    
    print("\n📊 Games with 65-74 confidence props:")
    for game, props in sorted(games_65_to_74.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"   {game}: {len(props)} props")
        for prop in props[:2]:
            print(f"      • {prop.prop.player_name} {prop.prop.stat_type} {prop.final_confidence}")
    
    print("\n" + "="*60)
    print(f"Total games with 75+ props: {len(games_75_plus)}")
    print(f"Total games with 65-74 props: {len(games_65_to_74)}")
    print(f"Total games with 65+ props: {len(games_75_plus) + len(games_65_to_74)}")

if __name__ == "__main__":
    check_variety()
