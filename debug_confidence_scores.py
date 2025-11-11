#!/usr/bin/env python
"""Debug confidence scores for all props"""

import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.WARNING)

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader

def main():
    print("\n" + "="*80)
    print("🔍 DEBUGGING CONFIDENCE SCORES - Week 8")
    print("="*80 + "\n")
    
    loader = NFLDataLoader(data_dir=str(Path(project_root) / "data"))
    analyzer = PropAnalyzer()
    
    # Load context
    print("📥 Loading data...")
    context = loader.load_all_data(week=8)
    props_list = context.get('props', [])
    print(f"✅ Loaded {len(props_list)} props\n")
    
    if not props_list:
        print("❌ No props loaded!")
        return
    
    # Analyze first 20 props in detail
    print("📊 Analyzing first 20 props in detail...\n")
    confidence_scores = []
    
    for idx, prop in enumerate(props_list[:20], 1):
        try:
            analysis = analyzer.analyze_prop(prop, context)
            if analysis:
                confidence_scores.append(analysis.final_confidence)
                
                print(f"{idx}. {analysis.prop.player_name} ({analysis.prop.team}) vs {analysis.prop.opponent}")
                print(f"   Stat: {analysis.prop.stat_type} O{analysis.prop.line}")
                print(f"   🎯 CONFIDENCE: {analysis.final_confidence}%")
                print(f"   📋 RECOMMENDATION: {analysis.recommendation}")
                
                # Show agent breakdown
                print(f"   Agent Breakdown:")
                for agent_name, result in sorted(analysis.agent_breakdown.items()):
                    raw_score = result.get('raw_score', 50)
                    weight = result.get('weight', 0)
                    print(f"      {agent_name}: {raw_score}/100 (weight: {weight})")
                print()
                
        except Exception as e:
            print(f"{idx}. ERROR analyzing prop: {e}\n")
    
    # Statistics
    print("\n" + "="*80)
    print("📈 CONFIDENCE SCORE STATISTICS")
    print("="*80)
    if confidence_scores:
        avg = sum(confidence_scores) / len(confidence_scores)
        min_conf = min(confidence_scores)
        max_conf = max(confidence_scores)
        print(f"Average Confidence: {avg:.1f}%")
        print(f"Min Confidence: {min_conf}%")
        print(f"Max Confidence: {max_conf}%")
        print(f"Sample Size: {len(confidence_scores)} props")
        
        # Count by threshold
        above_50 = sum(1 for c in confidence_scores if c >= 50)
        above_60 = sum(1 for c in confidence_scores if c >= 60)
        above_70 = sum(1 for c in confidence_scores if c >= 70)
        above_80 = sum(1 for c in confidence_scores if c >= 80)
        
        print(f"\nThreshold Counts:")
        print(f"  >= 50%: {above_50}")
        print(f"  >= 60%: {above_60}")
        print(f"  >= 70%: {above_70}")
        print(f"  >= 80%: {above_80}")
    else:
        print("❌ No props analyzed successfully")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
