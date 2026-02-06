#!/usr/bin/env python
"""
Agent Removal Analysis

Analyzes which agents should be removed entirely vs kept/inverted.
Criteria for removal:
1. Rarely provides signal (mostly returns 50 or None)
2. No predictive value even when inverted
3. Adds noise without improving accuracy
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def load_graded_results(weeks):
    results_dir = project_root / "data" / "backtest_results"
    all_results = []
    for week in weeks:
        graded_file = results_dir / f"graded_week_{week}.json"
        if graded_file.exists():
            with open(graded_file, 'r') as f:
                week_results = json.load(f)
                all_results.extend(week_results)
    return all_results


def analyze_agent_value(results):
    """Analyze each agent's contribution and predictive value."""

    agent_stats = defaultdict(lambda: {
        'total_appearances': 0,
        'neutral_scores': 0,  # Score == 50
        'strong_signals': 0,  # Score >= 65 or <= 35
        'agrees_wins': 0,
        'agrees_losses': 0,
        'disagrees_wins': 0,
        'disagrees_losses': 0,
        'score_distribution': defaultdict(int),
    })

    for r in results:
        agents = r.get('agents', {})
        final_direction = r.get('bet_type', '').upper()
        result = r.get('result', '').upper()

        for agent_name, agent_data in agents.items():
            stats = agent_stats[agent_name]
            stats['total_appearances'] += 1

            score = agent_data.get('raw_score', 50)
            direction = agent_data.get('direction', '').upper()

            # Track score distribution
            bucket = (score // 10) * 10
            stats['score_distribution'][bucket] += 1

            # Track neutral scores
            if score == 50:
                stats['neutral_scores'] += 1

            # Track strong signals
            if score >= 65 or score <= 35:
                stats['strong_signals'] += 1

            # Track accuracy
            if result in ('WIN', 'LOSS') and direction in ('OVER', 'UNDER'):
                agrees = (direction == final_direction)
                if agrees:
                    if result == 'WIN':
                        stats['agrees_wins'] += 1
                    else:
                        stats['agrees_losses'] += 1
                else:
                    if result == 'WIN':
                        stats['disagrees_wins'] += 1
                    else:
                        stats['disagrees_losses'] += 1

    return dict(agent_stats)


def print_analysis(agent_stats):
    print("\n" + "=" * 90)
    print("AGENT REMOVAL ANALYSIS")
    print("=" * 90)

    print("\n" + "-" * 90)
    print("SIGNAL QUALITY (How often does agent provide useful signal?)")
    print("-" * 90)
    print(f"{'Agent':<12s}  {'Appearances':>12s}  {'Neutral (50)':>14s}  {'Strong Signal':>14s}  {'Signal Rate':>12s}")
    print("-" * 90)

    rows = []
    for agent, stats in agent_stats.items():
        total = stats['total_appearances']
        neutral = stats['neutral_scores']
        strong = stats['strong_signals']
        signal_rate = ((total - neutral) / total * 100) if total > 0 else 0
        rows.append((agent, total, neutral, strong, signal_rate))

    rows.sort(key=lambda x: x[4], reverse=True)

    for agent, total, neutral, strong, signal_rate in rows:
        neutral_pct = neutral / total * 100 if total > 0 else 0
        strong_pct = strong / total * 100 if total > 0 else 0
        status = "LOW SIGNAL" if signal_rate < 50 else ""
        print(f"{agent:<12s}  {total:>12d}  {neutral:>6d} ({neutral_pct:>4.1f}%)  "
              f"{strong:>6d} ({strong_pct:>4.1f}%)  {signal_rate:>10.1f}%  {status}")

    print("\n" + "-" * 90)
    print("PREDICTIVE VALUE (Does the signal help or hurt?)")
    print("-" * 90)
    print(f"{'Agent':<12s}  {'Agrees':>18s}  {'Disagrees':>18s}  {'Best Use':>12s}  {'Recommendation':<20s}")
    print("-" * 90)

    recommendations = []
    for agent, stats in agent_stats.items():
        agrees_total = stats['agrees_wins'] + stats['agrees_losses']
        disagrees_total = stats['disagrees_wins'] + stats['disagrees_losses']

        if agrees_total >= 50 and disagrees_total >= 50:
            agrees_rate = stats['agrees_wins'] / agrees_total * 100
            disagrees_rate = stats['disagrees_wins'] / disagrees_total * 100

            if disagrees_rate > agrees_rate + 5:
                best_use = "INVERT"
                if disagrees_rate >= 55:
                    rec = "KEEP (inverted)"
                else:
                    rec = "CONSIDER REMOVAL"
            elif agrees_rate > disagrees_rate + 5:
                best_use = "NORMAL"
                if agrees_rate >= 55:
                    rec = "KEEP"
                else:
                    rec = "KEEP (low value)"
            else:
                best_use = "NEITHER"
                rec = "REMOVE (no value)"

            recommendations.append((agent, agrees_rate, agrees_total,
                                   disagrees_rate, disagrees_total, best_use, rec))

    recommendations.sort(key=lambda x: max(x[1], x[3]), reverse=True)

    for agent, agrees_rate, agrees_n, disagrees_rate, disagrees_n, best_use, rec in recommendations:
        print(f"{agent:<12s}  {agrees_rate:>5.1f}% ({agrees_n:>4d})    "
              f"{disagrees_rate:>5.1f}% ({disagrees_n:>4d})    {best_use:>12s}  {rec:<20s}")

    print("\n" + "-" * 90)
    print("SCORE DISTRIBUTION (What scores does each agent typically produce?)")
    print("-" * 90)

    for agent, stats in sorted(agent_stats.items()):
        dist = stats['score_distribution']
        total = stats['total_appearances']
        if total == 0:
            continue

        # Create simple histogram
        hist = []
        for bucket in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]:
            count = dist.get(bucket, 0)
            pct = count / total * 100
            if pct >= 5:
                hist.append(f"{bucket}s:{pct:.0f}%")

        print(f"{agent:<12s}: {', '.join(hist)}")

    print("\n" + "=" * 90)
    print("SUMMARY: AGENTS TO REMOVE")
    print("=" * 90)

    print("""
Based on the analysis:

REMOVE (no predictive value):
- Agents with ~50% accuracy in both directions (pure noise)
- Agents that rarely deviate from neutral (50)

KEEP BUT INVERT (contrarian value):
- Agents where disagreement significantly outperforms agreement

KEEP AS-IS (predictive value):
- Agents where agreement outperforms disagreement
""")


def main():
    weeks = list(range(11, 17))
    print(f"Loading data for weeks {weeks}...")
    results = load_graded_results(weeks)
    print(f"Loaded {len(results)} predictions")

    agent_stats = analyze_agent_value(results)
    print_analysis(agent_stats)


if __name__ == "__main__":
    main()
