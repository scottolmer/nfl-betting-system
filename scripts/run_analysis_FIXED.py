"""NFL Betting Analysis - FIXED (uses aggregated stats)"""

import sys
from pathlib import Path
import logging
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.stats_aggregator_FIXED import aggregate_historical_stats
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder

def run_analysis(week=8, skip_fetch=True):
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*70)
    print("🏈 NFL BETTING ANALYSIS SYSTEM")
    print("="*70)
    print(f"Week: {week} | Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Load data
    print("\n📂 STEP 2: LOADING NFL DATA")
    print("-"*70)
    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    context = loader.load_all_data(week=week)
    
    # Aggregate stats
    print("\n🔄 STEP 2.5: AGGREGATING HISTORICAL STATS")
    print("-"*70)
    aggregated_stats = aggregate_historical_stats(context)
    context['aggregated_stats'] = aggregated_stats  # KEY FIX
    print(f"✅ Aggregated stats for {len(aggregated_stats)} players")
    
    # Analyze
    print("\n🧠 STEP 3: ANALYZING PROPS")
    print("-"*70)
    analyzer = PropAnalyzer()
    all_analyses = analyzer.analyze_all_props(context, min_confidence=50)
    
    elite = [p for p in all_analyses if p.final_confidence >= 75]
    high = [p for p in all_analyses if 70 <= p.final_confidence < 75]
    good = [p for p in all_analyses if 65 <= p.final_confidence < 70]
    mod = [p for p in all_analyses if 60 <= p.final_confidence < 65]
    low = [p for p in all_analyses if p.final_confidence < 60]
    
    print(f"✅ Analyzed {len(all_analyses)} props")
    print(f"\n📊 Confidence Distribution:")
    print(f"   75-100 (🔥 ELITE):   {len(elite)}")
    print(f"   70-74  (⭐ HIGH):     {len(high)}")
    print(f"   65-69  (✅ GOOD):     {len(good)}")
    print(f"   60-64  (📊 MODERATE): {len(mod)}")
    print(f"   <60    (⚠️ LOW):      {len(low)}")
    
    # Build parlays
    print("\n🎯 STEP 5: BUILDING OPTIMAL PARLAYS")
    print("-"*70)
    parlay_builder = ParlayBuilder()
    parlays = parlay_builder.build_parlays(all_analyses, min_confidence=65)
    
    total = sum(len(p) for p in parlays.values())
    print(f"✅ Built {total} parlays")
    
    print("\n" + "="*70)
    print("🎉 COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--week', type=int, default=8)
    parser.add_argument('--skip-fetch', action='store_true', default=True)
    args = parser.parse_args()
    run_analysis(week=args.week, skip_fetch=args.skip_fetch)