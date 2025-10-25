"""
Show top confidence scores to diagnose why none hit 58+
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

print("Loading data...")
loader = NFLDataLoader(data_dir="data")
context = loader.load_all_data(week=7)

print(f"Analyzing {len(context['props'])} props...")
analyzer = PropAnalyzer()
all_analyses = analyzer.analyze_all_props(context, min_confidence=50)

print(f"\n✅ Found {len(all_analyses)} props with 50+ confidence")

# Sort by confidence
sorted_props = sorted(all_analyses, key=lambda x: x.final_confidence, reverse=True)

print("\n" + "="*80)
print("TOP 20 PROPS BY CONFIDENCE")
print("="*80)
print(f"{'Rank':<5} {'Player':<20} {'Stat':<12} {'Line':<8} {'Conf':<6} {'Team':<5}")
print("-"*80)

for i, prop in enumerate(sorted_props[:20], 1):
    print(f"{i:<5} {prop.prop.player_name[:20]:<20} {prop.prop.stat_type:<12} "
          f"{prop.prop.line:<8.1f} {prop.final_confidence:<6} {prop.prop.team:<5}")

print("\n" + "="*80)
print("CONFIDENCE DISTRIBUTION")
print("="*80)

# Count by range
ranges = [(50, 52), (52, 54), (54, 56), (56, 58), (58, 60), (60, 65), (65, 70), (70, 100)]
for low, high in ranges:
    count = sum(1 for p in all_analyses if low <= p.final_confidence < high)
    print(f"{low}-{high}: {count} props")

print(f"\nHighest confidence: {sorted_props[0].final_confidence if sorted_props else 0}")
print(f"Median confidence: {sorted_props[len(sorted_props)//2].final_confidence if sorted_props else 0}")
