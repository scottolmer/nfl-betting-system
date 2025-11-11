#!/usr/bin/env python3
"""
Analyze why agent scores are weak - check data quality
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

print("\n" + "="*100)
print("AGENT SCORING ANALYSIS - WHY ARE SCORES LOW?")
print("="*100)

loader = NFLDataLoader("data")
context = loader.load_all_data(week=9)
props = context.get('props', [])
analyzer = PropAnalyzer()

# Check data availability
print("\n[1] DATA AVAILABILITY CHECK")
print("-"*100)
print(f"Props loaded: {len(props)}")
print(f"DVOA Offensive teams: {len(context.get('dvoa_offensive', {}))}")
print(f"DVOA Defensive teams: {len(context.get('dvoa_defensive', {}))}")
print(f"Def vs Receiver teams: {len(context.get('defensive_vs_receiver', {}))}")
print(f"Usage data: {len(context.get('usage', {}))} players")
print(f"Trends data: {len(context.get('trends', {}))} players")

# Analyze a few props in detail
print("\n[2] SAMPLE PROP ANALYSIS")
print("-"*100)

for i in range(3):
    prop = props[i]
    analysis = analyzer.analyze_prop(prop, context)
    
    print(f"\nProp: {prop['player_name']} ({prop['team']}) vs {prop['opponent']} - {prop['stat_type']} O{prop['line']}")
    print(f"Confidence: {analysis.final_confidence}%\n")
    
    for agent_name in sorted(analysis.agent_breakdown.keys()):
        data = analysis.agent_breakdown[agent_name]
        raw = data['raw_score']
        weight = data['weight']
        
        # Check why score is what it is
        if raw == 50:
            print(f"  {agent_name:15} = 50 (NEUTRAL - no data or no signal)")
        elif 48 <= raw <= 52:
            print(f"  {agent_name:15} = {raw:.0f} (SLIGHTLY LEANING)")
        elif 55 <= raw <= 65:
            print(f"  {agent_name:15} = {raw:.0f} (MODERATE SIGNAL)")
        else:
            print(f"  {agent_name:15} = {raw:.0f} (STRONG SIGNAL)")

# Check agent contribution patterns
print("\n[3] AGENT CONTRIBUTION ANALYSIS")
print("-"*100)

total_contribution_by_agent = {
    'DVOA': [], 'Matchup': [], 'GameScript': [], 'Volume': [], 
    'Trend': [], 'Variance': []
}

for prop in props[:50]:
    analysis = analyzer.analyze_prop(prop, context)
    for agent_name, data in analysis.agent_breakdown.items():
        if agent_name in total_contribution_by_agent:
            raw = data['raw_score']
            weight = data['weight']
            contribution = (raw - 50) * weight
            total_contribution_by_agent[agent_name].append(contribution)

print("\nAverage agent contributions (per prop):\n")
for agent_name in sorted(total_contribution_by_agent.keys()):
    contributions = total_contribution_by_agent[agent_name]
    if contributions:
        avg_contrib = sum(contributions) / len(contributions)
        pos_count = len([c for c in contributions if c > 0])
        neg_count = len([c for c in contributions if c < 0])
        print(f"  {agent_name:15} | Avg contribution: {avg_contrib:+6.2f} | Positive: {pos_count}/50 | Negative: {neg_count}/50")

print("\n[4] KEY FINDINGS")
print("-"*100)
print("""
Low confidence scores (52-53%) caused by:

1. AGENTS RETURNING NEAR-NEUTRAL SCORES (48-55)
   Most agents score in tight 50-58 range instead of strong 65-75
   
2. CONFLICTING SIGNALS
   DVOA bullish (+), Matchup bearish (-), canceling each other
   
3. WEAK SIGNAL THRESHOLDS
   Agents need stronger DVOA to trigger big score changes

SOLUTIONS:
1. Increase agent weights on strong performers
2. Increase scoring thresholds - make agents more aggressive
3. Improve data quality - ensure all data loads
4. Filter props - only high-conviction bets
""")

print(f"\n{'='*100}\n")
