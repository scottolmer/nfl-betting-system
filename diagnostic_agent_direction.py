#!/usr/bin/env python3
"""
Agent Directional Scoring Diagnostic
Identifies why OVER and UNDER are getting identical confidence scores
"""

import sys
import os
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader

def diagnose_directional_scoring(week=12):
    """Analyze OVER/UNDER scoring asymmetry"""
    
    print("\n" + "="*80)
    print("🔍 AGENT DIRECTIONAL SCORING DIAGNOSTIC")
    print("="*80)
    
    loader = NFLDataLoader(data_dir=str(project_root / "data"))
    analyzer = PropAnalyzer()
    
    print(f"\n📊 Loading Week {week} data...")
    context = loader.load_all_data(week=week)
    
    print(f"📈 Analyzing all props...")
    all_analyses = analyzer.analyze_all_props(context, min_confidence=40)
    
    # Group by player/stat to find OVER/UNDER pairs
    prop_pairs = defaultdict(list)
    for analysis in all_analyses:
        prop = analysis.prop
        key = (prop.player_name.lower(), prop.stat_type)
        prop_pairs[key].append(analysis)
    
    # Find contradictory pairs (both high confidence)
    print("\n" + "="*80)
    print("🚨 CONTRADICTORY CONFIDENCE PAIRS (Both >60%)")
    print("="*80)
    
    contradictions = []
    for (player, stat), analyses in prop_pairs.items():
        if len(analyses) == 2:
            over = next((a for a in analyses if getattr(a.prop, 'bet_type', 'OVER') == 'OVER'), None)
            under = next((a for a in analyses if getattr(a.prop, 'bet_type', 'OVER') == 'UNDER'), None)
            
            if over and under:
                over_conf = over.final_confidence
                under_conf = under.final_confidence
                
                if over_conf >= 60 and under_conf >= 60 and abs(over_conf - under_conf) < 10:
                    contradictions.append({
                        'player': player,
                        'stat': stat,
                        'over_conf': over_conf,
                        'under_conf': under_conf,
                        'over_analysis': over,
                        'under_analysis': under
                    })
    
    print(f"\nFound {len(contradictions)} contradictory pairs:\n")
    
    for i, pair in enumerate(contradictions[:5], 1):
        print(f"{i}. {pair['player'].title()} {pair['stat']}")
        print(f"   OVER: {pair['over_conf']:.1f}%  |  UNDER: {pair['under_conf']:.1f}%")
        
        # Compare agent breakdown
        print(f"\n   Agent Breakdown Comparison:")
        print(f"   {'Agent':<15} {'OVER':<8} {'UNDER':<8} {'Diff':<8} {'Issue'}")
        print(f"   {'-'*60}")
        
        over_analysis = pair['over_analysis']
        under_analysis = pair['under_analysis']
        
        all_agents = set(over_analysis.agent_breakdown.keys()) | set(under_analysis.agent_breakdown.keys())
        
        for agent in sorted(all_agents):
            over_score = over_analysis.agent_breakdown.get(agent, 50)
            under_score = under_analysis.agent_breakdown.get(agent, 50)
            
            # Extract numeric if dict
            if isinstance(over_score, dict):
                over_score = over_score.get('raw_score', 50)
            if isinstance(under_score, dict):
                under_score = under_score.get('raw_score', 50)
            
            diff = abs(over_score - under_score)
            
            # Flag issues
            issue = ""
            if over_score == under_score:
                issue = "⚠️  IDENTICAL"
            elif diff < 5:
                issue = "⚠️  Too close"
            elif over_score > 60 and under_score > 60:
                issue = "❌ Both bullish"
            elif over_score < 40 and under_score < 40:
                issue = "❌ Both bearish"
            
            print(f"   {agent:<15} {over_score:<8.1f} {under_score:<8.1f} {diff:<8.1f} {issue}")
        
        print()
    
    # Summary
    print("\n" + "="*80)
    print("📊 ROOT CAUSE ANALYSIS")
    print("="*80)
    
    if len(contradictions) > 5:
        print(f"\n❌ {len(contradictions)} props show symmetric scoring")
        print("\nLikely causes:")
        print("1. Agents not inverting logic for UNDER bets")
        print("2. Agents returning same score regardless of bet direction")
        print("3. Agent weights applied equally to both directions")
        print("4. No penalty scaling for directional certainty")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    week = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    diagnose_directional_scoring(week)
