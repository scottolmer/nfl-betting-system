"""Run auto-learning on historical weeks using analyzed_props data"""

import sys
import io
import sqlite3
import json
from collections import defaultdict

# Fix encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, 'scripts/analysis')
from agent_weight_manager import AgentWeightManager

def get_analyzed_props_for_learning(week):
    """Get scored props from analyzed_props table"""
    conn = sqlite3.connect('bets.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT prop_id, player, prop_type, bet_type, result, agent_scores
        FROM analyzed_props
        WHERE week = ? AND result IS NOT NULL AND agent_scores IS NOT NULL
    ''', (week,))
    
    props = []
    for row in cursor.fetchall():
        prop_id, player, prop_type, bet_type, result, agent_scores = row
        try:
            scores = json.loads(agent_scores) if isinstance(agent_scores, str) else agent_scores
            props.append({
                'prop_id': prop_id,
                'player': player,
                'prop_type': prop_type,
                'bet_type': bet_type,
                'result': result,
                'agent_scores': scores
            })
        except Exception as e:
            continue
    
    conn.close()
    return props

def calculate_agent_performance(props):
    """Calculate agent performance from scored props"""
    agent_stats = defaultdict(lambda: {
        'predictions': [],
        'actuals': [],
        'hits': 0,
        'total': 0,
        'accuracy': 0,
        'overconfidence': 0,
        'sample_size': 0
    })
    
    for prop in props:
        actual = prop['result']  # 1 if hit, 0 if miss
        agent_scores = prop['agent_scores']
        
        for agent_name, score in agent_scores.items():
            # Convert agent score (0-100) to confidence (0-1)
            predicted_conf = score / 100.0
            agent_stats[agent_name]['predictions'].append(predicted_conf)
            agent_stats[agent_name]['actuals'].append(1 if actual else 0)
            agent_stats[agent_name]['total'] += 1
            
            if actual:
                agent_stats[agent_name]['hits'] += 1
    
    # Calculate metrics
    for agent_name, stats in agent_stats.items():
        if stats['total'] > 0:
            stats['sample_size'] = stats['total']
            stats['accuracy'] = stats['hits'] / stats['total']
            
            # Overconfidence: predicted higher than actual
            stats['overconfidence'] = (
                sum(stats['predictions']) / len(stats['predictions']) - stats['accuracy']
            )
    
    return dict(agent_stats)

print('='*80)
print('RUNNING AUTO-LEARNING ON HISTORICAL DATA')
print('='*80)
print()

manager = AgentWeightManager('bets.db')

for week in [10, 11, 12]:
    print(f'\n📊 WEEK {week} CALIBRATION')
    print('-'*80)
    
    # Get props for this week
    props = get_analyzed_props_for_learning(week)
    print(f'Found {len(props)} scored props for Week {week}')
    
    if len(props) == 0:
        print('⚠️ No scored props found, skipping...\n')
        continue
    
    # Calculate performance
    agent_performance = calculate_agent_performance(props)
    
    # Show summary
    print(f'\nAgent Performance Summary:')
    for agent_name in sorted(agent_performance.keys()):
        stats = agent_performance[agent_name]
        print(f'  {agent_name:12s}: {stats["accuracy"]:5.1%} accuracy, '
              f'{stats["overconfidence"]:+5.1%} overconf, '
              f'{stats["sample_size"]:3d} samples')
    
    # Apply adjustments
    print(f'\nApplying weight adjustments...')
    adjustments = manager.auto_adjust_weights(
        agent_performance=agent_performance,
        week=week,
        dry_run=False
    )
    
    # Show what changed
    for adj in adjustments:
        if adj['action'] != 'SKIP' and abs(adj.get('adjustment', 0)) > 0.01:
            symbol = '⬆️' if adj['adjustment'] > 0 else '⬇️'
            print(f"  {symbol} {adj['agent']:12s}: {adj['old_weight']:.2f} → {adj['new_weight']:.2f} "
                  f"({adj['adjustment']:+.2f})")
    
    print()

print('='*80)
print('✅ AUTO-LEARNING COMPLETE')
print('='*80)
print()

# Show final weights
manager.print_current_weights()
