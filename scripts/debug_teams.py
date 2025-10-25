"""Debug team matching"""
import sys
sys.path.append('.')
from scripts.analysis.data_loader import NFLDataLoader
from scripts.run_analysis import transform_dvoa_offensive, transform_dvoa_defensive, transform_betting_lines_to_props

loader = NFLDataLoader(data_dir='data')
context = loader.load_all_data(week=8)

# Transform
props = transform_betting_lines_to_props(context['betting_lines'], week=8)
dvoa_off = transform_dvoa_offensive(context['dvoa_off'])
dvoa_def = transform_dvoa_defensive(context['dvoa_def'])

print("="*60)
print("SAMPLE PROPS (first 3):")
print("="*60)
for prop in props[:3]:
    print(f"Player: {prop['player_name']}")
    print(f"  Team: '{prop['team']}'")
    print(f"  Opponent: '{prop['opponent']}'")
    print(f"  Stat: {prop['stat_type']} {prop['line']}")
    print()

print("="*60)
print("DVOA TEAMS (first 10):")
print("="*60)
for team in list(dvoa_off.keys())[:10]:
    print(f"  '{team}'")

print("\n" + "="*60)
print("TEAM MATCHING TEST:")
print("="*60)
test_team = props[0]['team']
test_opp = props[0]['opponent']
print(f"Prop team: '{test_team}'")
print(f"  In DVOA Off? {test_team in dvoa_off}")
print(f"Prop opponent: '{test_opp}'")
print(f"  In DVOA Def? {test_opp in dvoa_def}")
