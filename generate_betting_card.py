"""
Generate actionable parlay betting card with game diversity
"""

import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent  # Script is in project root
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder

def diversify_props(all_analyses):
    """Round-robin selection from each game for diversity"""
    if not all_analyses:
        return []
    
    games = {}
    for analysis in all_analyses:
        game = f"{analysis.prop.team} vs {analysis.prop.opponent}"
        if game not in games:
            games[game] = []
        games[game].append(analysis)
    
    if not games:
        return []
    
    for game in games:
        games[game].sort(key=lambda x: x.final_confidence, reverse=True)
    
    diversified = []
    max_rounds = max(len(props) for props in games.values())
    
    for round_num in range(max_rounds):
        for game, props in sorted(games.items(), key=lambda x: len(x[1]), reverse=True):
            if round_num < len(props):
                diversified.append(props[round_num])
    
    return diversified

def generate_betting_card(week=9, min_confidence=65):
    print("\n" + "="*60)
    print(f"🏈 WEEK {week} NFL PARLAY BETTING CARD")
    print("="*60)
    print()
    
    print(f"📂 Loading Week {week} data...")
    data_dir = project_root / "data"
    loader = NFLDataLoader(data_dir=str(data_dir))
    context = loader.load_all_data(week=week)
    
    print("🧠 Analyzing props...")
    analyzer = PropAnalyzer()
    all_analyses = analyzer.analyze_all_props(context, min_confidence=50)
    
    print(f"✅ Found {len(all_analyses)} quality props")
    
    print("🔄 Diversifying for game variety...")
    diversified_analyses = diversify_props(all_analyses)
    
    print(f"🎯 Building optimal parlays (min {min_confidence}% confidence)...")
    parlay_builder = ParlayBuilder()
    parlays = parlay_builder.build_parlays(diversified_analyses, min_confidence=min_confidence)
    
    betting_card = parlay_builder.format_parlays_for_betting(parlays)
    print(betting_card)
    
    # Save with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = project_root / "data" / "betting_history" / f"week_{week}" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "betting_card.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(betting_card)
    
    # Also save latest
    latest_file = project_root / "data" / f"week{week}_betting_card.txt"
    with open(latest_file, 'w', encoding='utf-8') as f:
        f.write(betting_card)
    
    print(f"\n✅ Saved to: {output_file}")
    print(f"✅ Latest: {latest_file}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    total_2leg = len(parlays.get('2-leg', []))
    total_3leg = len(parlays.get('3-leg', []))
    total_4leg = len(parlays.get('4-leg', []))
    
    print(f"2-leg: {total_2leg}")
    print(f"3-leg: {total_3leg}")
    print(f"4-leg: {total_4leg}")
    print(f"Total parlays: {total_2leg + total_3leg + total_4leg}")
    
    total_units = sum(p.recommended_units for pl in parlays.values() for p in pl)
    print(f"\nRecommended units: {total_units:.1f}")
    print(f"At $10/unit: ${total_units * 10:.0f}")
    print(f"At $25/unit: ${total_units * 25:.0f}")
    
    # Top plays
    print("\n" + "="*60)
    print("🔥 TOP 5 INDIVIDUAL PROPS")
    print("="*60)
    
    for i, analysis in enumerate(all_analyses[:5], 1):
        prop = analysis.prop
        print(f"\n{i}. {prop.player_name} - {prop.stat_type} OVER {prop.line}")
        print(f"   {prop.team} vs {prop.opponent}")
        print(f"   Confidence: {analysis.final_confidence}%")
        for reason in analysis.rationale[:2]:
            print(f"      • {reason}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Generate betting card')
    parser.add_argument('--week', type=int, default=9, help='NFL week')
    parser.add_argument('--min-conf', type=int, default=65, help='Min confidence')
    args = parser.parse_args()
    
    generate_betting_card(week=args.week, min_confidence=args.min_conf)
