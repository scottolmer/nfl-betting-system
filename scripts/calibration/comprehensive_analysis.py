#!/usr/bin/env python
"""
Comprehensive Season Analysis

Runs multiple analyses on graded backtest data to identify actionable patterns.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def load_graded_results(weeks: List[int]) -> List[dict]:
    """Load all graded results from specified weeks."""
    results_dir = project_root / "data" / "backtest_results"
    all_results = []

    for week in weeks:
        graded_file = results_dir / f"graded_week_{week}.json"
        if graded_file.exists():
            with open(graded_file, 'r') as f:
                week_results = json.load(f)
                for r in week_results:
                    r['week'] = week
                all_results.extend(week_results)

    return all_results


def analyze_stat_types(results: List[dict]) -> Dict:
    """Analyze performance by stat type."""
    stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'voids': 0})

    for r in results:
        stat_type = r.get('stat_type', 'Unknown')
        result = r.get('result', '').upper()

        if result == 'WIN':
            stats[stat_type]['wins'] += 1
        elif result == 'LOSS':
            stats[stat_type]['losses'] += 1
        else:
            stats[stat_type]['voids'] += 1

    return dict(stats)


def analyze_over_under_bias(results: List[dict]) -> Dict:
    """Analyze over vs under performance."""
    bias = {
        'OVER': {'wins': 0, 'losses': 0},
        'UNDER': {'wins': 0, 'losses': 0}
    }

    by_stat = defaultdict(lambda: {
        'OVER': {'wins': 0, 'losses': 0},
        'UNDER': {'wins': 0, 'losses': 0}
    })

    for r in results:
        bet_type = r.get('bet_type', '').upper()
        result = r.get('result', '').upper()
        stat_type = r.get('stat_type', 'Unknown')

        if bet_type in ('OVER', 'UNDER') and result in ('WIN', 'LOSS'):
            if result == 'WIN':
                bias[bet_type]['wins'] += 1
                by_stat[stat_type][bet_type]['wins'] += 1
            else:
                bias[bet_type]['losses'] += 1
                by_stat[stat_type][bet_type]['losses'] += 1

    return {'overall': bias, 'by_stat': dict(by_stat)}


def analyze_agent_performance(results: List[dict]) -> Dict:
    """Analyze individual agent predictive power."""
    agent_stats = defaultdict(lambda: {
        'correct_direction': 0,
        'wrong_direction': 0,
        'strong_correct': 0,  # score >= 70 and correct
        'strong_wrong': 0,    # score >= 70 and wrong
    })

    for r in results:
        agents = r.get('agents', {})
        final_direction = r.get('bet_type', '').upper()
        result = r.get('result', '').upper()

        if result not in ('WIN', 'LOSS'):
            continue

        for agent_name, agent_data in agents.items():
            agent_dir = agent_data.get('direction', '').upper()
            agent_score = agent_data.get('raw_score', 50)

            if agent_dir in ('OVER', 'UNDER'):
                # Did agent agree with final bet direction?
                agreed = (agent_dir == final_direction)

                # Was the final bet correct?
                bet_correct = (result == 'WIN')

                # Agent was "right" if: agreed with winning bet OR disagreed with losing bet
                agent_correct = (agreed and bet_correct) or (not agreed and not bet_correct)

                if agent_correct:
                    agent_stats[agent_name]['correct_direction'] += 1
                    if agent_score >= 70:
                        agent_stats[agent_name]['strong_correct'] += 1
                else:
                    agent_stats[agent_name]['wrong_direction'] += 1
                    if agent_score >= 70:
                        agent_stats[agent_name]['strong_wrong'] += 1

    return dict(agent_stats)


def analyze_agent_agreement(results: List[dict]) -> Dict:
    """Analyze performance based on how many agents agree."""
    agreement_stats = defaultdict(lambda: {'wins': 0, 'losses': 0})

    for r in results:
        agents = r.get('agents', {})
        final_direction = r.get('bet_type', '').upper()
        result = r.get('result', '').upper()

        if result not in ('WIN', 'LOSS'):
            continue

        # Count agents agreeing with final direction
        agreeing = 0
        total_agents = 0

        for agent_name, agent_data in agents.items():
            agent_dir = agent_data.get('direction', '').upper()
            if agent_dir in ('OVER', 'UNDER'):
                total_agents += 1
                if agent_dir == final_direction:
                    agreeing += 1

        if total_agents > 0:
            agreement_pct = int(agreeing / total_agents * 100)
            bucket = f"{(agreement_pct // 20) * 20}-{(agreement_pct // 20) * 20 + 20}%"

            if result == 'WIN':
                agreement_stats[bucket]['wins'] += 1
            else:
                agreement_stats[bucket]['losses'] += 1

    return dict(agreement_stats)


def analyze_line_ranges(results: List[dict]) -> Dict:
    """Analyze performance by line value ranges."""
    # Group by stat type and line range
    line_stats = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0}))

    for r in results:
        stat_type = r.get('stat_type', 'Unknown')
        line = r.get('line', 0)
        result = r.get('result', '').upper()

        if result not in ('WIN', 'LOSS'):
            continue

        # Create line bucket based on stat type
        if 'Yards' in stat_type:
            bucket_size = 20
        elif 'Attempts' in stat_type or 'Receptions' in stat_type or 'Completions' in stat_type:
            bucket_size = 5
        else:
            bucket_size = 1

        bucket_start = int(line // bucket_size) * bucket_size
        bucket = f"{bucket_start}-{bucket_start + bucket_size}"

        if result == 'WIN':
            line_stats[stat_type][bucket]['wins'] += 1
        else:
            line_stats[stat_type][bucket]['losses'] += 1

    return {k: dict(v) for k, v in line_stats.items()}


def print_stat_type_analysis(stats: Dict):
    """Print stat type performance."""
    print("\n" + "=" * 70)
    print("STAT TYPE PERFORMANCE")
    print("=" * 70)
    print(f"{'Stat Type':<25s}  {'Wins':>6s}  {'Losses':>6s}  {'Total':>6s}  {'Win Rate':>10s}")
    print("-" * 70)

    rows = []
    for stat_type, data in stats.items():
        total = data['wins'] + data['losses']
        if total > 0:
            win_rate = data['wins'] / total * 100
            rows.append((stat_type, data['wins'], data['losses'], total, win_rate))

    # Sort by sample size
    rows.sort(key=lambda x: x[3], reverse=True)

    for stat_type, wins, losses, total, win_rate in rows:
        marker = " **" if win_rate >= 55 else " !!" if win_rate < 45 else ""
        print(f"{stat_type:<25s}  {wins:>6d}  {losses:>6d}  {total:>6d}  {win_rate:>9.1f}%{marker}")

    print("-" * 70)
    print("** = Strong performer (55%+)   !! = Weak performer (<45%)")


def print_over_under_analysis(bias: Dict):
    """Print over/under bias analysis."""
    print("\n" + "=" * 70)
    print("OVER/UNDER BIAS ANALYSIS")
    print("=" * 70)

    overall = bias['overall']
    print("\nOverall:")
    for bet_type in ['OVER', 'UNDER']:
        data = overall[bet_type]
        total = data['wins'] + data['losses']
        rate = data['wins'] / total * 100 if total > 0 else 0
        print(f"  {bet_type}: {rate:.1f}% ({data['wins']}W/{data['losses']}L)")

    print("\nBy Stat Type (showing significant bias only):")
    print("-" * 70)

    by_stat = bias['by_stat']
    for stat_type, data in sorted(by_stat.items()):
        over_total = data['OVER']['wins'] + data['OVER']['losses']
        under_total = data['UNDER']['wins'] + data['UNDER']['losses']

        if over_total >= 20 and under_total >= 20:
            over_rate = data['OVER']['wins'] / over_total * 100
            under_rate = data['UNDER']['wins'] / under_total * 100
            diff = over_rate - under_rate

            if abs(diff) >= 5:  # Only show significant bias
                better = "OVER" if diff > 0 else "UNDER"
                print(f"  {stat_type:<25s}: {better} wins {abs(diff):.1f}% more often")
                print(f"      OVER: {over_rate:.1f}% ({data['OVER']['wins']}W/{data['OVER']['losses']}L)")
                print(f"      UNDER: {under_rate:.1f}% ({data['UNDER']['wins']}W/{data['UNDER']['losses']}L)")


def print_agent_analysis(agent_stats: Dict):
    """Print agent performance analysis."""
    print("\n" + "=" * 70)
    print("AGENT PREDICTIVE POWER")
    print("=" * 70)
    print(f"{'Agent':<12s}  {'Overall Acc':>12s}  {'Strong Signal Acc':>18s}  {'Assessment':<15s}")
    print("-" * 70)

    rows = []
    for agent, data in agent_stats.items():
        total = data['correct_direction'] + data['wrong_direction']
        strong_total = data['strong_correct'] + data['strong_wrong']

        if total > 0:
            overall_acc = data['correct_direction'] / total * 100
            strong_acc = data['strong_correct'] / strong_total * 100 if strong_total > 0 else 0

            # Assessment
            if strong_acc >= 55 and strong_total >= 50:
                assessment = "VALUABLE"
            elif strong_acc >= 50 and strong_total >= 50:
                assessment = "Useful"
            elif strong_acc < 45 and strong_total >= 50:
                assessment = "REDUCE WEIGHT"
            else:
                assessment = "Needs data"

            rows.append((agent, overall_acc, total, strong_acc, strong_total, assessment))

    rows.sort(key=lambda x: x[3], reverse=True)

    for agent, overall_acc, total, strong_acc, strong_total, assessment in rows:
        print(f"{agent:<12s}  {overall_acc:>10.1f}% ({total:>4d})  "
              f"{strong_acc:>10.1f}% ({strong_total:>4d})      {assessment:<15s}")

    print("-" * 70)
    print("Strong Signal = agent score >= 70")


def print_agreement_analysis(agreement_stats: Dict):
    """Print agent agreement analysis."""
    print("\n" + "=" * 70)
    print("AGENT AGREEMENT IMPACT")
    print("=" * 70)
    print("Win rate by % of agents agreeing with final bet direction:")
    print("-" * 70)
    print(f"{'Agreement':>12s}  {'Wins':>6s}  {'Losses':>6s}  {'Win Rate':>10s}")
    print("-" * 70)

    buckets = ['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
    for bucket in buckets:
        if bucket in agreement_stats:
            data = agreement_stats[bucket]
            total = data['wins'] + data['losses']
            rate = data['wins'] / total * 100 if total > 0 else 0
            print(f"{bucket:>12s}  {data['wins']:>6d}  {data['losses']:>6d}  {rate:>9.1f}%")

    print("-" * 70)
    print("Higher agreement = more agent consensus on direction")


def print_line_analysis(line_stats: Dict):
    """Print line range analysis for key stat types."""
    print("\n" + "=" * 70)
    print("LINE VALUE SWEET SPOTS (top stat types)")
    print("=" * 70)

    # Show top 4 stat types by sample size
    stat_totals = {}
    for stat_type, buckets in line_stats.items():
        total = sum(d['wins'] + d['losses'] for d in buckets.values())
        stat_totals[stat_type] = total

    top_stats = sorted(stat_totals.items(), key=lambda x: x[1], reverse=True)[:4]

    for stat_type, _ in top_stats:
        print(f"\n{stat_type}:")
        print("-" * 50)

        buckets = line_stats[stat_type]
        rows = []
        for bucket, data in buckets.items():
            total = data['wins'] + data['losses']
            if total >= 20:  # Minimum sample
                rate = data['wins'] / total * 100
                rows.append((bucket, data['wins'], data['losses'], total, rate))

        rows.sort(key=lambda x: float(x[0].split('-')[0]))

        for bucket, wins, losses, total, rate in rows:
            marker = " **" if rate >= 55 else " !!" if rate < 45 else ""
            print(f"  {bucket:>12s}: {rate:>5.1f}% ({wins}W/{losses}L){marker}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Comprehensive season analysis')
    parser.add_argument('--weeks', '-w', type=str, default='11-16')
    args = parser.parse_args()

    if '-' in args.weeks:
        start, end = args.weeks.split('-')
        weeks = list(range(int(start), int(end) + 1))
    else:
        weeks = [int(w) for w in args.weeks.split(',')]

    print(f"Loading data for weeks {weeks}...")
    results = load_graded_results(weeks)
    print(f"Loaded {len(results)} predictions\n")

    # Run analyses
    stat_stats = analyze_stat_types(results)
    print_stat_type_analysis(stat_stats)

    bias = analyze_over_under_bias(results)
    print_over_under_analysis(bias)

    agent_stats = analyze_agent_performance(results)
    print_agent_analysis(agent_stats)

    agreement = analyze_agent_agreement(results)
    print_agreement_analysis(agreement)

    line_stats = analyze_line_ranges(results)
    print_line_analysis(line_stats)

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
