#!/usr/bin/env python
"""Test dependency analyzer"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from scripts.analysis.dependency_analyzer import DependencyAnalyzer
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.parlay_builder import ParlayBuilder

load_dotenv()


def main():
    # Parse week argument - handle "week 8" or "8"
    week = int(os.environ.get('NFL_WEEK', 8))
    
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'week' and len(sys.argv) > 2:
            week = int(sys.argv[2])
        else:
            try:
                week = int(sys.argv[1])
            except ValueError:
                pass
    
    print("\n" + "="*70)
    print("🧪 DEPENDENCY ANALYZER TEST")
    print("="*70)
    
    print(f"\n📊 Loading week {week} data...")
    loader = NFLDataLoader(data_dir=str(Path(__file__).parent / "data"))
    context = loader.load_all_data(week=week)
    
    print("📊 Analyzing props...")
    analyzer = PropAnalyzer()
    props = analyzer.analyze_all_props(context, min_confidence=60)
    print(f"   ✅ {len(props)} props analyzed")
    
    print("🎰 Building parlays...")
    builder = ParlayBuilder()
    
    # Diversify props
    games = {}
    for p in props:
        g = f"{p.prop.team} vs {p.prop.opponent}"
        if g not in games:
            games[g] = []
        games[g].append(p)
    
    for g in games:
        games[g].sort(key=lambda x: x.final_confidence, reverse=True)
    
    diversified = []
    max_rounds = max(len(v) for v in games.values()) if games else 0
    for round_num in range(max_rounds):
        for g, plist in sorted(games.items(), key=lambda x: len(x[1]), reverse=True):
            if round_num < len(plist):
                diversified.append(plist[round_num])
    
    parlays = builder.build_parlays(diversified, min_confidence=65)
    total = sum(len(p) for p in parlays.values())
    print(f"   ✅ {total} parlays built")
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n❌ ERROR: ANTHROPIC_API_KEY not set in .env")
        sys.exit(1)
    
    print("\n🔍 Analyzing dependencies with Claude...\n")
    dep_analyzer = DependencyAnalyzer(api_key=api_key)
    result = dep_analyzer.analyze_all_parlays(parlays)
    
    report = dep_analyzer.generate_dependency_report(result)
    print(report)
    
    print_adjusted_recommendations(result)


def print_adjusted_recommendations(analyzed_parlays):
    """Print parlays with adjusted confidence scores"""
    
    print("\n" + "="*70)
    print("🎯 ADJUSTED PARLAY RECOMMENDATIONS")
    print("="*70)
    
    total_units = 0
    total_parlays = 0
    
    for parlay_type in ['2-leg', '3-leg', '4-leg', '5-leg']:
        items = analyzed_parlays.get(parlay_type, [])
        if not items:
            continue
        
        print(f"\n{parlay_type.upper()} PARLAYS ({len(items)} total)")
        print("-" * 70)
        
        for i, item in enumerate(items, 1):
            parlay = item['parlay']
            analysis = item['dependency_analysis']
            
            orig_conf = parlay.combined_confidence
            adj_conf = analysis.get('adjusted_confidence', 50)
            recommendation = analysis.get('recommendation', 'REVIEW')
            adjustment = analysis.get('correlation_adjustment', {}).get('adjustment_value', 0)
            
            total_parlays += 1
            
            # Determine units
            if recommendation == "AVOID":
                units = 0
                emoji = "❌"
            elif recommendation == "MODIFY":
                units = max(0.25, parlay.recommended_units * 0.75)
                emoji = "⚠️"
            else:
                units = parlay.recommended_units
                emoji = "✅"
            
            total_units += units
            
            print(f"\n{emoji} PARLAY {i} ({recommendation})")
            print(f"   Confidence: {orig_conf}% → {adj_conf}% ({adjustment:+d})")
            print(f"   Bet: {units:.2f} units (${units*10:.0f})")
            
            for j, leg in enumerate(parlay.legs, 1):
                print(f"     {j}. {leg.prop.player_name} - {leg.prop.stat_type} OVER {leg.prop.line}")
    
    print("\n" + "="*70)
    print(f"Total: {total_parlays} parlays | {total_units:.1f} units | ${total_units*10:.0f}")
    print("="*70)


if __name__ == '__main__':
    main()
