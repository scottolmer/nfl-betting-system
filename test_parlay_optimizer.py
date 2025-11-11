#!/usr/bin/env python
"""Test parlay optimizer - builds low-correlation parlays"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from scripts.analysis.parlay_optimizer import ParlayOptimizer
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.dependency_analyzer import DependencyAnalyzer

load_dotenv()


def main():
    # Parse week
    week = int(os.environ.get('NFL_WEEK', 9))
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == 'week' and len(sys.argv) > 2:
            week = int(sys.argv[2])
        else:
            try:
                week = int(sys.argv[1])
            except ValueError:
                pass
    
    print("\n" + "="*70)
    print("🔄 PARLAY OPTIMIZER - LOW CORRELATION TEST")
    print("="*70)
    
    print(f"\n📊 Loading week {week} data...")
    loader = NFLDataLoader(data_dir=str(Path(__file__).parent / "data"))
    context = loader.load_all_data(week=week)
    
    print("📊 Analyzing props...")
    analyzer = PropAnalyzer()
    props = analyzer.analyze_all_props(context, min_confidence=60)
    print(f"   ✅ {len(props)} props analyzed")
    
    # Check API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n❌ ERROR: ANTHROPIC_API_KEY not set in .env")
        sys.exit(1)
    
    # Optimize parlays
    optimizer = ParlayOptimizer(api_key=api_key)
    optimized_parlays = optimizer.rebuild_parlays_low_correlation(
        props,
        target_parlays=10,
        min_confidence=65
    )
    
    # Analyze with dependency analyzer to get analyzed results
    print("\n🔍 Re-analyzing with dependencies...\n")
    dep_analyzer = DependencyAnalyzer(api_key=api_key)
    analyzed = dep_analyzer.analyze_all_parlays(optimized_parlays)
    
    # Get best parlays from analyzed data
    best = []
    for ptype in ['2-leg', '3-leg', '4-leg', '5-leg']:
        for item in analyzed.get(ptype, []):
            analysis = item['dependency_analysis']
            rec = analysis.get('recommendation')
            
            if rec != "AVOID":
                best.append({
                    'parlay': item['parlay'],
                    'adjusted_confidence': analysis.get('adjusted_confidence'),
                    'recommendation': rec,
                    'adjustment': analysis.get('correlation_adjustment', {}).get('adjustment_value', 0)
                })
    
    best.sort(key=lambda x: x['adjusted_confidence'], reverse=True)
    
    # Format and print
    output = optimizer.format_best_parlays(best)
    print(output)
    
    print("\n💡 KEY INSIGHTS:")
    print("   • Parlays rebuilt prioritizing prop independence")
    print("   • Multiple games and players per parlay = lower correlation")
    print("   • Adjusted confidence reflects real win probability")
    print("   • Only ACCEPT/MODIFY parlays shown (AVOID filtered out)")


if __name__ == '__main__':
    main()
