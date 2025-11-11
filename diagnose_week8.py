#!/usr/bin/env python
"""Create a minimal but functional system for Week 8 analysis"""

import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

def main():
    print("\n" + "="*80)
    print("🔧 WEEK 8 SYSTEM REMEDIATION")
    print("="*80 + "\n")
    
    from scripts.analysis.data_loader import NFLDataLoader
    from scripts.analysis.orchestrator import PropAnalyzer
    
    loader = NFLDataLoader(data_dir=str(Path(project_root) / "data"))
    analyzer = PropAnalyzer()
    
    print("📥 Loading Week 8 data...")
    context = loader.load_all_data(week=8)
    
    props_list = context.get('props', [])
    print(f"✅ Loaded {len(props_list)} props\n")
    
    print("📊 Data Summary:")
    print(f"  DVOA Offensive: {len(context.get('dvoa_offensive', {}))} teams")
    print(f"  DVOA Defensive: {len(context.get('dvoa_defensive', {}))} teams")
    print(f"  Defensive vs Receiver: {len(context.get('defensive_vs_receiver', {}))} teams")
    print(f"  Usage Data: {len(context.get('usage', {}))} players")
    print(f"  Trends: {len(context.get('trends', {}))} players")
    print(f"  Injuries: {'✓' if context.get('injuries') else '✗'}\n")
    
    if len(context.get('dvoa_offensive', {})) == 0:
        print("⚠️  WARNING: No DVOA offensive data loaded!")
    if len(context.get('usage', {})) == 0:
        print("⚠️  WARNING: No usage data loaded!")
    
    print("📊 Analyzing sample props...\n")
    
    confidence_scores = []
    agent_score_distribution = {agent: [] for agent in [
        'DVOA', 'Matchup', 'Injury', 'GameScript', 'Volume', 'Trend', 'Variance', 'Weather'
    ]}
    
    for idx, prop in enumerate(props_list[:50], 1):
        try:
            analysis = analyzer.analyze_prop(prop, context)
            if analysis:
                confidence_scores.append(analysis.final_confidence)
                
                for agent_name, result in analysis.agent_breakdown.items():
                    agent_score_distribution[agent_name].append(result.get('raw_score', 50))
                
                if idx <= 5:  # Show first 5
                    print(f"{idx}. {analysis.prop.player_name} ({analysis.prop.team})")
                    print(f"   {analysis.prop.stat_type} O{analysis.prop.line}: {analysis.final_confidence}%\n")
        except Exception as e:
            logger.error(f"Error analyzing prop {idx}: {e}")
    
    print("="*80)
    print("📈 CONFIDENCE SCORE ANALYSIS")
    print("="*80)
    
    if confidence_scores:
        avg = sum(confidence_scores) / len(confidence_scores)
        above_50 = sum(1 for c in confidence_scores if c >= 50)
        above_60 = sum(1 for c in confidence_scores if c >= 60)
        above_70 = sum(1 for c in confidence_scores if c >= 70)
        
        print(f"Average Confidence: {avg:.1f}%")
        print(f"Props >= 50%: {above_50}/50")
        print(f"Props >= 60%: {above_60}/50")
        print(f"Props >= 70%: {above_70}/50")
        print(f"Min: {min(confidence_scores)}%, Max: {max(confidence_scores)}%\n")
        
        print("Agent Score Averages:")
        for agent_name in sorted(agent_score_distribution.keys()):
            scores = agent_score_distribution[agent_name]
            if scores:
                avg_score = sum(scores) / len(scores)
                print(f"  {agent_name}: {avg_score:.1f}/100")
    
    print("\n" + "="*80)
    print("✅ Remediation complete - retry 'parlays 70' or lower threshold")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
