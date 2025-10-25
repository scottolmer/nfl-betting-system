import sys
sys.path.insert(0, '.')

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.stats_aggregator_FIXED import aggregate_historical_stats
from scripts.run_analysis_FIXED import transform_betting_lines_to_props

loader = NFLDataLoader('data')
context = loader.load_all_data(8)
context = aggregate_historical_stats(context)

print("Checking name formats:")
print("\nFirst 10 players in usage dict:")
for i, name in enumerate(list(context['usage'].keys())[:10]):
    print(f"  '{name}'")
    if i == 9:
        break

print("\nSearching for 'jefferson' in usage:")
jefferson_names = [k for k in context['usage'].keys() if 'jefferson' in k.lower()]
print(jefferson_names)

context['props'] = transform_betting_lines_to_props(context['betting_lines'], 8)

print("\nFirst 5 prop player names:")
for i, prop in enumerate(context['props'][:5]):
    print(f"  '{prop['player_name']}'")
