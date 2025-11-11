#!/usr/bin/env python
"""Diagnostic script to check confidence distribution at different thresholds"""

import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader

loader = NFLDataLoader(data_dir=str(project_root / "data"))
analyzer = PropAnalyzer()

week = 9
print(f"\n📊 Analyzing confidence scores for Week {week}...\n")

# Load data
context = loader.load_all_data(week=week)
props_list = context.get('props', [])
print(f"Total props loaded: {len(props_list)}\n")

# Analyze all props
all_analyses = []
for i, prop in enumerate(props_list, 1):
    if i % 100 == 0:
        print(f"Progress: {i}/{len(props_list)}")
    try:
        analysis = analyzer.analyze_prop(prop, context)
        if analysis:
            all_analyses.append(analysis)
    except Exception as e:
        pass

print(f"\nSuccessfully analyzed: {len(all_analyses)} props\n")

# Group by confidence ranges
confidence_buckets = {}
for analysis in all_analyses:
    conf = analysis.final_confidence
    bucket = f"{int(conf // 10) * 10}-{int(conf // 10) * 10 + 9}"
    if bucket not in confidence_buckets:
        confidence_buckets[bucket] = []
    confidence_buckets[bucket].append(analysis)

print("📊 CONFIDENCE DISTRIBUTION:")
print("="*60)
for bucket in sorted(confidence_buckets.keys()):
    count = len(confidence_buckets[bucket])
    pct = (count / len(all_analyses)) * 100
    print(f"{bucket}%: {count:3d} props ({pct:5.1f}%)")

print("="*60)

# Show threshold breakdown
thresholds = [50, 55, 60, 65, 70, 75, 80]
print("\n📊 PROPS ABOVE CONFIDENCE THRESHOLD:")
print("="*60)
for threshold in thresholds:
    above = [a for a in all_analyses if a.final_confidence >= threshold]
    pct = (len(above) / len(all_analyses)) * 100
    print(f"≥ {threshold}%: {len(above):3d} props ({pct:5.1f}%)")

print("="*60)

# Show bottom 20 props
print("\n⚠️  BOTTOM 20 PROPS (Lowest Confidence):")
print("="*60)
bottom = sorted(all_analyses, key=lambda x: x.final_confidence)[:20]
for i, analysis in enumerate(bottom, 1):
    prop = analysis.prop
    print(f"{i:2d}. {prop.player_name:20s} {prop.stat_type:12s} @ {prop.line:5.1f} - {analysis.final_confidence:5.1f}%")

print("\n✅ Diagnostic complete")
