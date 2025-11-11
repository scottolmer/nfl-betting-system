#!/usr/bin/env python3
"""
Show improvement after disabling non-functional agents
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

print("\n" + "="*100)
print("CONFIDENCE SCORES AFTER AGENT FIX")
print("="*100)

loader = NFLDataLoader("data")
context = loader.load_all_data(week=9)
props = context.get('props', [])

analyzer = PropAnalyzer()

print("\nAnalyzing first 100 props...\n")

confidence_scores = []
for prop in props[:100]:
    analysis = analyzer.analyze_prop(prop, context)
    confidence_scores.append(analysis.final_confidence)

avg_conf = sum(confidence_scores) / len(confidence_scores)
min_conf = min(confidence_scores)
max_conf = max(confidence_scores)

print(f"Results after disabling Injury & Weather agents:\n")
print(f"  Average confidence: {avg_conf:.1f}% (was 52.5%)")
print(f"  Min: {min_conf:.1f}%")
print(f"  Max: {max_conf:.1f}%")
print(f"  Count >= 70: {len([c for c in confidence_scores if c >= 70])}")
print(f"  Count >= 65: {len([c for c in confidence_scores if c >= 65])}")
print(f"  Count >= 60: {len([c for c in confidence_scores if c >= 60])}")
print(f"  Count >= 55: {len([c for c in confidence_scores if c >= 55])}")

improvement = avg_conf - 52.5
print(f"\n  Improvement: +{improvement:.1f} percentage points")

if improvement > 5:
    print(f"\n✓ SIGNIFICANT improvement! Removing non-functional agents worked.")
elif improvement > 0:
    print(f"\n✓ Modest improvement from removing dead-weight agents.")
else:
    print(f"\n⚠️ No improvement - other issues may exist.")

print(f"\n{'='*100}\n")
