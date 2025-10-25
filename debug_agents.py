import sys
sys.path.insert(0, '.')

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.stats_aggregator_FIXED import aggregate_historical_stats
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.run_analysis_FIXED import transform_betting_lines_to_props

print("Loading data...")
loader = NFLDataLoader('data')
context = loader.load_all_data(8)
print(f"\nBefore aggregation - historical_stats weeks: {list(context.get('historical_stats', {}).keys())}")

context = aggregate_historical_stats(context)

print(f"\nAfter aggregation:")
print(f"  Players in usage: {len(context['usage'])}")

# Check a WR who should have data
test_players = ['ja\'marr chase', 'justin jefferson', 'ceedee lamb']
for player in test_players:
    if player in context['usage']:
        print(f"\n  {player}:")
        print(f"    {context['usage'][player]}")
        break

context['props'] = transform_betting_lines_to_props(context['betting_lines'], 8)

print("\nAnalyzing prop...")
analyzer = PropAnalyzer()

# Find a receiving prop
for prop in context['props']:
    if 'rec' in prop['stat_type'].lower():
        print(f"Prop: {prop['player_name']} - {prop['stat_type']} {prop['line']}")
        result = analyzer.analyze_prop(prop, context)
        print(f"\nFinal Confidence: {result.final_confidence}")
        print(f"\nAgent Breakdown:")
        for agent_name, score in result.agent_breakdown.items():
            print(f"  {agent_name:20s}: {score}")
        break
