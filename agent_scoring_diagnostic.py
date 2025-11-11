#!/usr/bin/env python3
"""
Diagnostic: Analyze agent scoring for week 9 props
Check if all agents are contributing properly
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer

print("\n" + "="*100)
print("AGENT SCORING DIAGNOSTIC - WEEK 9")
print("="*100)

# Load data
print("\n[1] Loading week 9 data...")
loader = NFLDataLoader("data")
context = loader.load_all_data(week=9)

props = context.get('props', [])
print(f"✓ Loaded {len(props)} props")
print(f"  Usage data: {len(context.get('usage', {}))} players")
print(f"  Trends data: {len(context.get('trends', {}))} players")

# Initialize analyzer
analyzer = PropAnalyzer()

# Analyze first 5 props to see agent breakdown
print("\n[2] Analyzing sample props to check agent scores...\n")

for i in range(min(5, len(props))):
    prop = props[i]
    analysis = analyzer.analyze_prop(prop, context)
    
    print(f"{'='*100}")
    print(f"PROP {i+1}: {prop['player_name'].upper()} ({prop['team']}) vs {prop['opponent']}")
    print(f"         {prop['stat_type']} O{prop['line']}")
    print(f"{'='*100}")
    print(f"FINAL CONFIDENCE: {analysis.final_confidence}%")
    print(f"\nAGENT BREAKDOWN:")
    
    agent_scores = {}
    for agent_name, agent_data in sorted(analysis.agent_breakdown.items(), 
                                         key=lambda x: x[1]['raw_score'], reverse=True):
        raw = agent_data['raw_score']
        weight = agent_data['weight']
        contribution = (raw - 50) * weight if weight > 0 else 0
        agent_scores[agent_name] = {
            'raw': raw,
            'weight': weight,
            'contribution': contribution
        }
        
        status = "✓" if raw != 50 else "⚠"
        print(f"  {status} {agent_name:20} | Raw: {raw:6.1f} | Weight: {weight:6.1f} | Contribution: {contribution:+7.2f}")
        
        # Show rationale if available
        if agent_data.get('rationale'):
            for rationale in agent_data['rationale'][:2]:
                print(f"      └─ {rationale}")
    
    print()

# Summary analysis
print(f"\n{'='*100}")
print("SUMMARY ANALYSIS")
print(f"{'='*100}\n")

# Analyze multiple props to find patterns
print("[3] Analyzing all props to identify patterns...\n")

agent_neutral_count = {agent: 0 for agent in ['DVOA', 'Matchup', 'Volume', 'Injury', 'Trend', 'GameScript', 'Variance', 'Weather']}
agent_stats = {agent: {'scores': [], 'contributions': []} for agent in agent_neutral_count.keys()}
confidence_scores = []
all_weights = {agent: [] for agent in agent_neutral_count.keys()}

sample_size = min(100, len(props))
print(f"Sampling {sample_size} props...\n")

for prop in props[:sample_size]:
    analysis = analyzer.analyze_prop(prop, context)
    confidence_scores.append(analysis.final_confidence)
    
    for agent_name, agent_data in analysis.agent_breakdown.items():
        raw_score = agent_data['raw_score']
        weight = agent_data['weight']
        
        if agent_name not in agent_stats:
            agent_stats[agent_name] = {'scores': [], 'contributions': []}
        
        agent_stats[agent_name]['scores'].append(raw_score)
        all_weights[agent_name].append(weight)
        
        if raw_score == 50:
            agent_neutral_count[agent_name] += 1

# Print summary
print("Agent Performance (first 100 props):\n")
for agent_name in sorted(agent_stats.keys()):
    if agent_name in agent_neutral_count:
        neutral = agent_neutral_count[agent_name]
        avg_score = sum(agent_stats[agent_name]['scores']) / len(agent_stats[agent_name]['scores'])
        avg_weight = sum(all_weights[agent_name]) / len(all_weights[agent_name])
        
        status = "✓" if neutral < 20 else "⚠" if neutral < 50 else "❌"
        print(f"{status} {agent_name:15} | Neutral (50): {neutral:3}/{sample_size} | Avg Score: {avg_score:6.1f} | Avg Weight: {avg_weight:6.1f}")

print(f"\nConfidence Scores (first {sample_size} props):")
avg_conf = sum(confidence_scores) / len(confidence_scores)
min_conf = min(confidence_scores)
max_conf = max(confidence_scores)
print(f"  Average: {avg_conf:.1f}%")
print(f"  Min: {min_conf:.1f}%")
print(f"  Max: {max_conf:.1f}%")
print(f"  Count >= 70: {len([c for c in confidence_scores if c >= 70])}")
print(f"  Count >= 60: {len([c for c in confidence_scores if c >= 60])}")
print(f"  Count >= 55: {len([c for c in confidence_scores if c >= 55])}")

# Check for issues
print(f"\n{'='*100}")
print("DIAGNOSIS")
print(f"{'='*100}\n")

issues_found = False

for agent_name in agent_neutral_count:
    neutral_count = agent_neutral_count[agent_name]
    if neutral_count > 50:
        print(f"❌ {agent_name}: {neutral_count}/{sample_size} props returning NEUTRAL (50) score")
        print(f"   This agent is NOT contributing effectively!")
        issues_found = True

if avg_conf < 55:
    print(f"⚠️  Average confidence is {avg_conf:.1f}%")
    if avg_conf < 50:
        print(f"   This suggests agents are not providing strong OVER signals")
    else:
        print(f"   This might indicate balanced but weak agent contributions")
    issues_found = True
elif avg_conf < 60:
    print(f"⚠️  Average confidence is {avg_conf:.1f}%")
    print(f"   Confidence is moderate - agents could be stronger")
    issues_found = True

if not issues_found:
    print(f"✓ All agents appear to be scoring correctly!")
    print(f"✓ Average confidence of {avg_conf:.1f}% is reasonable for diverse prop pool")

print(f"\n{'='*100}")
print("RECOMMENDATIONS")
print(f"{'='*100}\n")

if avg_conf < 55:
    print("If confidence scores are too low:")
    print("  1. Check if USAGE and TRENDS data are loading properly")
    print("  2. Verify DVOA data is available and correct")
    print("  3. Consider increasing agent weights for stronger signals")
    print("  4. Review injury data - ensure it's being parsed correctly")
elif avg_conf < 60:
    print("Confidence is slightly low. Consider:")
    print("  1. Increasing weights on strong agents (DVOA, Matchup)")
    print("  2. Ensuring all historical data is loaded (usage, trends)")
    print("  3. Calibrating agent thresholds based on historical performance")
else:
    print("Confidence levels look reasonable.")
    print("Next steps:")
    print("  1. Filter for highest confidence props (70+)")
    print("  2. Build parlays from these high-confidence picks")
    print("  3. Backtest against historical results")

print(f"\n{'='*100}\n")
