"""
Generate actionable parlay betting card for Week 7 (WITH GAME DIVERSITY)
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder

def diversify_props(all_analyses, min_per_game=5):
    """
    Reorder props to ensure game diversity.
    Takes top props from each game in round-robin fashion.
    """
    # Group by game
    games = {}
    for analysis in all_analyses:
        game = f"{analysis.prop.team} vs {analysis.prop.opponent}"
        if game not in games:
            games[game] = []
        games[game].append(analysis)
    
    # Sort each game's props by confidence
    for game in games:
        games[game].sort(key=lambda x: x.final_confidence, reverse=True)
    
    # Round-robin selection
    diversified = []
    max_rounds = max(len(props) for props in games.values())
    
    for round_num in range(max_rounds):
        for game, props in sorted(games.items(), key=lambda x: len(x[1]), reverse=True):
            if round_num < len(props):
                diversified.append(props[round_num])
    
    return diversified

def generate_betting_card():
    print("\n" + "="*60)
    print("🏈 WEEK 7 NFL PARLAY BETTING CARD")
    print("="*60)
    print()
    
    # Load data
    print("📂 Loading Week 7 data...")
    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    context = loader.load_all_data(week=7)
    
    # Analyze props
    print("🧠 Analyzing props...")
    analyzer = PropAnalyzer()
    all_analyses = analyzer.analyze_all_props(context, min_confidence=50)
    
    print(f"✅ Found {len(all_analyses)} quality props")
    
    # Diversify props for better game variety
    print("🔄 Diversifying prop list for game variety...")
    diversified_analyses = diversify_props(all_analyses)
    print(f"✅ Reordered {len(diversified_analyses)} props across games")
    print()
    
    # Build parlays (use 65 for more variety across games)
    print("🎯 Building optimal parlays...")
    parlay_builder = ParlayBuilder()
    parlays = parlay_builder.build_parlays(diversified_analyses, min_confidence=65)
    
    # Format and display
    betting_card = parlay_builder.format_parlays_for_betting(parlays)
    print(betting_card)
    
    # Save to file (with UTF-8 encoding for emojis)
    output_file = project_root / "data" / "week7_betting_card.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(betting_card)
    
    print(f"\n✅ Betting card saved to: {output_file}")
    print()
    
    # Show quick summary
    print("="*60)
    print("📊 QUICK SUMMARY")
    print("="*60)
    
    total_2leg = len(parlays.get('2-leg', []))
    total_3leg = len(parlays.get('3-leg', []))
    total_4leg = len(parlays.get('4-leg', []))
    
    print(f"2-leg parlays: {total_2leg}")
    print(f"3-leg parlays: {total_3leg}")
    print(f"4-leg parlays: {total_4leg}")
    print(f"Total parlays: {total_2leg + total_3leg + total_4leg}")
    
    # Calculate total recommended investment
    total_units = 0
    for parlay_list in parlays.values():
        for parlay in parlay_list:
            total_units += parlay.recommended_units
    
    print(f"\nTotal recommended units: {total_units:.1f}")
    print(f"At $10/unit: ${total_units * 10:.0f}")
    print(f"At $25/unit: ${total_units * 25:.0f}")
    print()
    
    # Show top confidence plays
    print("="*60)
    print("🔥 TOP 5 INDIVIDUAL PROPS (if you prefer singles)")
    print("="*60)
    
    for i, analysis in enumerate(all_analyses[:5], 1):
        prop = analysis.prop
        print(f"\n{i}. {prop.player_name} - {prop.stat_type} OVER {prop.line}")
        print(f"   {prop.team} vs {prop.opponent}")
        print(f"   Confidence: {analysis.final_confidence}")
        print(f"   Top reasons:")
        for reason in analysis.rationale[:2]:
            print(f"      • {reason}")
    
    print("\n" + "="*60)
    print("✅ Betting card generation complete!")
    print("="*60)

if __name__ == "__main__":
    generate_betting_card()
