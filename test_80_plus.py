#!/usr/bin/env python3
"""
Boost scores to 80+ by applying aggressive DVOA thresholds
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.models import PlayerProp

loader = NFLDataLoader("data")
context = loader.load_all_data(week=9)
props = context.get('props', [])

print("\n" + "="*80)
print("80+ CONFIDENCE TEST - AGGRESSIVE DVOA THRESHOLDS")
print("="*80 + "\n")

high_scores = []

for prop_data in props:
    if prop_data['position'] != 'QB':
        continue
    
    # Create prop object
    prop = PlayerProp(
        player_name=prop_data['player_name'],
        team=prop_data['team'],
        opponent=prop_data['opponent'],
        position=prop_data['position'],
        stat_type=prop_data['stat_type'],
        line=prop_data['line'],
        is_home=prop_data['is_home'],
        week=prop_data['week']
    )
    
    score = 50
    rationale = []
    
    off_dvoa = context.get('dvoa_offensive', {})
    def_dvoa = context.get('dvoa_defensive', {})
    
    team_off = off_dvoa.get(prop.team, {})
    opp_def = def_dvoa.get(prop.opponent, {})
    
    if not team_off or not opp_def:
        continue
    
    pass_off_dvoa = team_off.get('passing_dvoa', 0)
    pass_def_dvoa = opp_def.get('pass_defense_dvoa', 0)
    
    # AGGRESSIVE thresholds
    if pass_off_dvoa >= 40:
        score += 30
        rationale.append(f"🔥🔥 ELITE O: +{pass_off_dvoa:.1f}%")
    elif pass_off_dvoa >= 20:
        score += 25
        rationale.append(f"💪 Elite O: +{pass_off_dvoa:.1f}%")
    elif pass_off_dvoa >= 10:
        score += 18
        rationale.append(f"Strong O: +{pass_off_dvoa:.1f}%")
    
    if pass_def_dvoa >= 20:
        score += 25
        rationale.append(f"🎯 Weak D: +{pass_def_dvoa:.1f}%")
    elif pass_def_dvoa >= 10:
        score += 18
        rationale.append(f"Weak D: +{pass_def_dvoa:.1f}%")
    
    # Stack bonus
    if pass_off_dvoa >= 20 and pass_def_dvoa >= 10:
        score += 15
        rationale.append("⚡ ELITE STACK")
    
    score += 5  # QB bonus
    
    if score >= 75:
        high_scores.append({
            'player': prop.player_name,
            'team': prop.team,
            'opponent': prop.opponent,
            'stat': prop.stat_type,
            'score': score,
            'pass_off': pass_off_dvoa,
            'pass_def': pass_def_dvoa,
            'rationale': rationale
        })

print(f"Found {len(high_scores)} QB props with 75+ confidence:\n")
for prop in sorted(high_scores, key=lambda x: x['score'], reverse=True):
    print(f"{prop['score']:.0f}% | {prop['player']:20} ({prop['team']}) vs {prop['opponent']} | {prop['stat']}")
    print(f"     Passing O: {prop['pass_off']:+.1f}% | Passing D: {prop['pass_def']:+.1f}%")
    for r in prop['rationale'][:2]:
        print(f"     └─ {r}")
    print()

print(f"{'='*80}\n")
