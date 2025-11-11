#!/usr/bin/env python
"""Verify all 8 agents are scoring correctly"""

import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.WARNING)

project_root = Path.cwd()
sys.path.insert(0, str(project_root))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

def main():
    print("\n" + "="*80)
    print("🔍 AGENT VERIFICATION - All 8 Agents")
    print("="*80 + "\n")
    
    loader = NFLDataLoader(data_dir=str(Path(project_root) / "data"))
    analyzer = PropAnalyzer()
    
    context = loader.load_all_data(week=8)
    props_list = context.get('props', [])
    
    print(f"📥 Loaded {len(props_list)} props\n")
    print("📊 Context Data Available:")
    print(f"  DVOA Offensive: {len(context.get('dvoa_offensive', {}))} teams")
    print(f"  DVOA Defensive: {len(context.get('dvoa_defensive', {}))} teams")
    print(f"  Def vs Receiver: {len(context.get('defensive_vs_receiver', {}))} teams")
    print(f"  Usage: {len(context.get('usage', {}))} players")
    print(f"  Trends: {len(context.get('trends', {}))} players")
    print(f"  Injuries: {'Yes' if context.get('injuries') else 'No'}\n")
    
    # Analyze first 5 props in detail
    print("="*80)
    print("DETAILED AGENT BREAKDOWN - First 5 Props")
    print("="*80 + "\n")
    
    agent_names = ['DVOA', 'Matchup', 'Injury', 'GameScript', 'Volume', 'Trend', 'Variance', 'Weather']
    agent_stats = {agent: {'scores': [], 'weights': [], 'with_rationale': 0} for agent in agent_names}
    
    for idx, prop in enumerate(props_list[:5], 1):
        try:
            analysis = analyzer.analyze_prop(prop, context)
            
            print(f"\n{'='*80}")
            print(f"PROP {idx}: {analysis.prop.player_name} ({analysis.prop.team}) vs {analysis.prop.opponent}")
            print(f"Stat: {analysis.prop.stat_type} O{analysis.prop.line}")
            print(f"Game Total: {analysis.prop.game_total} | Spread: {analysis.prop.spread}")
            print(f"{'='*80}")
            print(f"📊 FINAL CONFIDENCE: {analysis.final_confidence}% | Recommendation: {analysis.recommendation}\n")
            
            print("AGENT SCORES:")
            print(f"{'Agent':<15} {'Score':<8} {'Weight':<8} {'Rationale':<50}")
            print("-" * 80)
            
            for agent_name in agent_names:
                result = analysis.agent_breakdown.get(agent_name, {})
                score = result.get('raw_score', 50)
                weight = result.get('weight', 0)
                rationale = result.get('rationale', [])
                rationale_str = (rationale[0][:47] + "...") if rationale else "No rationale"
                
                print(f"{agent_name:<15} {score:<8.0f} {weight:<8.1f} {rationale_str:<50}")
                
                # Collect stats
                agent_stats[agent_name]['scores'].append(score)
                agent_stats[agent_name]['weights'].append(weight)
                if rationale:
                    agent_stats[agent_name]['with_rationale'] += 1
        
        except Exception as e:
            print(f"ERROR analyzing prop {idx}: {e}")
    
    # Summary statistics
    print("\n" + "="*80)
    print("AGENT SUMMARY STATISTICS (First 5 props)")
    print("="*80 + "\n")
    
    print(f"{'Agent':<15} {'Avg Score':<12} {'Weight':<10} {'W/ Rationale':<15} {'Status':<20}")
    print("-" * 80)
    
    for agent_name in agent_names:
        stats = agent_stats[agent_name]
        if stats['scores']:
            avg_score = sum(stats['scores']) / len(stats['scores'])
            weight = stats['weights'][0] if stats['weights'] else 0
            with_rationale = stats['with_rationale']
            
            # Determine status
            if avg_score != 50:
                status = "✅ SCORING (not neutral)"
            elif with_rationale > 0:
                status = "✅ PROVIDING RATIONALE"
            else:
                status = "⚠️ ALL NEUTRAL (50)"
            
            print(f"{agent_name:<15} {avg_score:<12.1f} {weight:<10.1f} {with_rationale}/5 {status:<20}")
        else:
            print(f"{agent_name:<15} {'N/A':<12} {'N/A':<10} {'N/A':<15} {'⚠️ NOT RUN':<20}")
    
    print("\n" + "="*80)
    print("INTERPRETATION")
    print("="*80)
    print("""
✅ GOOD SIGNS:
  • All agents have weight > 0
  • Most agents show non-neutral scores
  • Agents provide rationale for recommendations

⚠️ CONCERNS:
  • Any agent scoring all 50s indicates data/logic issue
  • All agents with same score suggests averaging problem
  • Missing rationale means agent isn't making decisions

Note: Agents can score 50 legitimately (e.g., Injury when no injuries, 
      Volume when no usage data available). Check rationale field.
    """)

if __name__ == "__main__":
    main()
