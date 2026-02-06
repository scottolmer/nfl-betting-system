#!/usr/bin/env python
"""
Agent Disagreement Analysis

Investigates why high agent agreement correlates with WORSE performance.
Possible hypotheses:
1. When all agents agree, the line has already moved to price in obvious factors
2. Certain "bad" agents agreeing is actually a negative signal
3. Disagreement from specific agents is actually valuable (contrarian signal)

This script tests these hypotheses.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
from itertools import combinations

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


def analyze_individual_agent_agreement(results: List[dict]) -> Dict:
    """
    For each agent: what's the win rate when it agrees vs disagrees with final bet?

    Hypothesis: "Bad" agents (Matchup, Volume) disagreeing might be a positive signal.
    """
    agent_stats = defaultdict(lambda: {
        'agrees_wins': 0, 'agrees_losses': 0,
        'disagrees_wins': 0, 'disagrees_losses': 0
    })

    for r in results:
        agents = r.get('agents', {})
        final_direction = r.get('bet_type', '').upper()
        result = r.get('result', '').upper()

        if result not in ('WIN', 'LOSS'):
            continue

        for agent_name, agent_data in agents.items():
            agent_dir = agent_data.get('direction', '').upper()

            if agent_dir not in ('OVER', 'UNDER'):
                continue

            agrees = (agent_dir == final_direction)

            if agrees:
                if result == 'WIN':
                    agent_stats[agent_name]['agrees_wins'] += 1
                else:
                    agent_stats[agent_name]['agrees_losses'] += 1
            else:
                if result == 'WIN':
                    agent_stats[agent_name]['disagrees_wins'] += 1
                else:
                    agent_stats[agent_name]['disagrees_losses'] += 1

    return dict(agent_stats)


def analyze_contrarian_signals(results: List[dict]) -> Dict:
    """
    When a specific agent disagrees with the consensus, what happens?

    This helps identify which agents provide valuable contrarian signals.
    """
    contrarian_stats = defaultdict(lambda: {'wins': 0, 'losses': 0})

    for r in results:
        agents = r.get('agents', {})
        final_direction = r.get('bet_type', '').upper()
        result = r.get('result', '').upper()

        if result not in ('WIN', 'LOSS'):
            continue

        # Count how many agents agree with final direction
        agreeing_agents = []
        disagreeing_agents = []

        for agent_name, agent_data in agents.items():
            agent_dir = agent_data.get('direction', '').upper()
            if agent_dir in ('OVER', 'UNDER'):
                if agent_dir == final_direction:
                    agreeing_agents.append(agent_name)
                else:
                    disagreeing_agents.append(agent_name)

        # For each disagreeing agent, track outcomes
        for agent in disagreeing_agents:
            key = f"{agent}_disagrees"
            if result == 'WIN':
                contrarian_stats[key]['wins'] += 1
            else:
                contrarian_stats[key]['losses'] += 1

    return dict(contrarian_stats)


def analyze_agent_pair_agreement(results: List[dict]) -> Dict:
    """
    When specific pairs of agents agree/disagree, what's the win rate?

    Helps identify which agent combinations are predictive.
    """
    pair_stats = defaultdict(lambda: {
        'both_agree_wins': 0, 'both_agree_losses': 0,
        'both_disagree_wins': 0, 'both_disagree_losses': 0,
        'split_wins': 0, 'split_losses': 0
    })

    agents_of_interest = ['DVOA', 'Matchup', 'Volume', 'Injury', 'HitRate']

    for r in results:
        agents = r.get('agents', {})
        final_direction = r.get('bet_type', '').upper()
        result = r.get('result', '').upper()

        if result not in ('WIN', 'LOSS'):
            continue

        # Get agent directions
        agent_dirs = {}
        for agent_name in agents_of_interest:
            if agent_name in agents:
                agent_dir = agents[agent_name].get('direction', '').upper()
                if agent_dir in ('OVER', 'UNDER'):
                    agent_dirs[agent_name] = (agent_dir == final_direction)

        # Check all pairs
        for a1, a2 in combinations(agents_of_interest, 2):
            if a1 not in agent_dirs or a2 not in agent_dirs:
                continue

            pair_key = f"{a1}+{a2}"
            a1_agrees = agent_dirs[a1]
            a2_agrees = agent_dirs[a2]

            if a1_agrees and a2_agrees:
                category = 'both_agree'
            elif not a1_agrees and not a2_agrees:
                category = 'both_disagree'
            else:
                category = 'split'

            if result == 'WIN':
                pair_stats[pair_key][f'{category}_wins'] += 1
            else:
                pair_stats[pair_key][f'{category}_losses'] += 1

    return dict(pair_stats)


def analyze_good_vs_bad_agent_split(results: List[dict]) -> Dict:
    """
    What happens when "good" agents (Injury, DVOA, Variance) agree
    but "bad" agents (Matchup, Volume) disagree?

    This tests if filtering out bad agent signals improves predictions.
    """
    stats = {
        'good_agree_bad_disagree': {'wins': 0, 'losses': 0},
        'good_disagree_bad_agree': {'wins': 0, 'losses': 0},
        'all_good_agree': {'wins': 0, 'losses': 0},
        'all_bad_agree': {'wins': 0, 'losses': 0},
    }

    good_agents = ['Injury', 'DVOA', 'Variance']
    bad_agents = ['Matchup', 'Volume']

    for r in results:
        agents = r.get('agents', {})
        final_direction = r.get('bet_type', '').upper()
        result = r.get('result', '').upper()

        if result not in ('WIN', 'LOSS'):
            continue

        # Check good agents
        good_agreeing = 0
        good_total = 0
        for agent_name in good_agents:
            if agent_name in agents:
                agent_dir = agents[agent_name].get('direction', '').upper()
                if agent_dir in ('OVER', 'UNDER'):
                    good_total += 1
                    if agent_dir == final_direction:
                        good_agreeing += 1

        # Check bad agents
        bad_agreeing = 0
        bad_total = 0
        for agent_name in bad_agents:
            if agent_name in agents:
                agent_dir = agents[agent_name].get('direction', '').upper()
                if agent_dir in ('OVER', 'UNDER'):
                    bad_total += 1
                    if agent_dir == final_direction:
                        bad_agreeing += 1

        # Categorize
        if good_total >= 2 and bad_total >= 1:
            good_majority = good_agreeing >= (good_total / 2)
            bad_majority = bad_agreeing >= (bad_total / 2)

            if good_majority and not bad_majority:
                category = 'good_agree_bad_disagree'
            elif not good_majority and bad_majority:
                category = 'good_disagree_bad_agree'
            elif good_majority and bad_majority:
                category = 'all_good_agree'  # Using this for "all agree" case
            else:
                continue  # Skip when neither group has majority

            if result == 'WIN':
                stats[category]['wins'] += 1
            else:
                stats[category]['losses'] += 1

    return stats


def analyze_confidence_with_disagreement(results: List[dict]) -> Dict:
    """
    Does the relationship between confidence and win rate change
    based on agent agreement level?
    """
    stats = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0}))

    for r in results:
        agents = r.get('agents', {})
        final_direction = r.get('bet_type', '').upper()
        result = r.get('result', '').upper()
        confidence = r.get('confidence', 50)

        if result not in ('WIN', 'LOSS'):
            continue

        # Calculate agreement %
        agreeing = 0
        total = 0
        for agent_name, agent_data in agents.items():
            agent_dir = agent_data.get('direction', '').upper()
            if agent_dir in ('OVER', 'UNDER'):
                total += 1
                if agent_dir == final_direction:
                    agreeing += 1

        if total == 0:
            continue

        agreement_pct = agreeing / total * 100

        # Bucket agreement
        if agreement_pct >= 80:
            agreement_bucket = 'high (80%+)'
        elif agreement_pct >= 50:
            agreement_bucket = 'medium (50-80%)'
        else:
            agreement_bucket = 'low (<50%)'

        # Bucket confidence
        if confidence >= 75:
            conf_bucket = '75%+'
        elif confidence >= 60:
            conf_bucket = '60-75%'
        else:
            conf_bucket = '<60%'

        if result == 'WIN':
            stats[agreement_bucket][conf_bucket]['wins'] += 1
        else:
            stats[agreement_bucket][conf_bucket]['losses'] += 1

    return {k: dict(v) for k, v in stats.items()}


def print_analysis(results: List[dict]):
    """Run and print all analyses."""

    print("\n" + "=" * 80)
    print("AGENT DISAGREEMENT DEEP DIVE")
    print("=" * 80)
    print(f"\nTotal predictions analyzed: {len(results)}")

    # Analysis 1: Individual agent agreement impact
    print("\n" + "-" * 80)
    print("ANALYSIS 1: Win Rate When Each Agent Agrees vs Disagrees")
    print("-" * 80)
    print("Question: Which agents are BETTER to disagree with?\n")

    agent_stats = analyze_individual_agent_agreement(results)

    rows = []
    for agent, stats in agent_stats.items():
        agrees_total = stats['agrees_wins'] + stats['agrees_losses']
        disagrees_total = stats['disagrees_wins'] + stats['disagrees_losses']

        if agrees_total >= 50 and disagrees_total >= 50:
            agrees_rate = stats['agrees_wins'] / agrees_total * 100
            disagrees_rate = stats['disagrees_wins'] / disagrees_total * 100
            diff = disagrees_rate - agrees_rate
            rows.append((agent, agrees_rate, agrees_total, disagrees_rate, disagrees_total, diff))

    rows.sort(key=lambda x: x[5], reverse=True)

    print(f"{'Agent':<12s}  {'Agrees':>18s}  {'Disagrees':>18s}  {'Diff':>8s}  {'Signal':<20s}")
    print("-" * 80)

    for agent, agrees_rate, agrees_n, disagrees_rate, disagrees_n, diff in rows:
        signal = ""
        if diff > 5:
            signal = "CONTRARIAN VALUE"
        elif diff < -5:
            signal = "Agreement helps"

        print(f"{agent:<12s}  {agrees_rate:>5.1f}% ({agrees_n:>4d})    "
              f"{disagrees_rate:>5.1f}% ({disagrees_n:>4d})    {diff:>+6.1f}%  {signal:<20s}")

    # Analysis 2: Good vs Bad agent split
    print("\n" + "-" * 80)
    print("ANALYSIS 2: Good Agents vs Bad Agents")
    print("-" * 80)
    print("Good agents: Injury, DVOA, Variance (higher accuracy)")
    print("Bad agents: Matchup, Volume (lower accuracy)\n")

    split_stats = analyze_good_vs_bad_agent_split(results)

    print(f"{'Scenario':<35s}  {'Wins':>6s}  {'Losses':>6s}  {'Win Rate':>10s}")
    print("-" * 65)

    for scenario, stats in split_stats.items():
        total = stats['wins'] + stats['losses']
        if total > 0:
            rate = stats['wins'] / total * 100
            label = scenario.replace('_', ' ').title()
            print(f"{label:<35s}  {stats['wins']:>6d}  {stats['losses']:>6d}  {rate:>9.1f}%")

    # Analysis 3: Contrarian signals
    print("\n" + "-" * 80)
    print("ANALYSIS 3: Contrarian Agent Signals")
    print("-" * 80)
    print("Win rate when specific agent DISAGREES with final bet\n")

    contrarian = analyze_contrarian_signals(results)

    rows = []
    for key, stats in contrarian.items():
        total = stats['wins'] + stats['losses']
        if total >= 100:
            rate = stats['wins'] / total * 100
            agent = key.replace('_disagrees', '')
            rows.append((agent, rate, total, stats['wins'], stats['losses']))

    rows.sort(key=lambda x: x[1], reverse=True)

    print(f"{'Agent Disagrees':<20s}  {'Win Rate':>10s}  {'Sample':>8s}")
    print("-" * 45)

    for agent, rate, total, wins, losses in rows:
        marker = " ** CONTRARIAN" if rate > 55 else ""
        print(f"{agent:<20s}  {rate:>9.1f}%  ({wins}W/{losses}L){marker}")

    # Analysis 4: Agent pairs
    print("\n" + "-" * 80)
    print("ANALYSIS 4: Agent Pair Interactions")
    print("-" * 80)
    print("When both agents agree vs both disagree vs split\n")

    pair_stats = analyze_agent_pair_agreement(results)

    # Find most interesting pairs (biggest spread between agree and disagree)
    interesting_pairs = []
    for pair, stats in pair_stats.items():
        both_agree_total = stats['both_agree_wins'] + stats['both_agree_losses']
        both_disagree_total = stats['both_disagree_wins'] + stats['both_disagree_losses']

        if both_agree_total >= 50 and both_disagree_total >= 50:
            agree_rate = stats['both_agree_wins'] / both_agree_total * 100
            disagree_rate = stats['both_disagree_wins'] / both_disagree_total * 100
            spread = disagree_rate - agree_rate
            interesting_pairs.append((pair, agree_rate, both_agree_total,
                                      disagree_rate, both_disagree_total, spread))

    interesting_pairs.sort(key=lambda x: abs(x[5]), reverse=True)

    print(f"{'Pair':<20s}  {'Both Agree':>15s}  {'Both Disagree':>15s}  {'Spread':>8s}")
    print("-" * 65)

    for pair, agree_rate, agree_n, disagree_rate, disagree_n, spread in interesting_pairs[:10]:
        print(f"{pair:<20s}  {agree_rate:>5.1f}% ({agree_n:>3d})   "
              f"{disagree_rate:>5.1f}% ({disagree_n:>3d})    {spread:>+6.1f}%")

    # Analysis 5: Confidence x Agreement interaction
    print("\n" + "-" * 80)
    print("ANALYSIS 5: Confidence vs Agreement Interaction")
    print("-" * 80)
    print("Does high confidence + low agreement = better outcome?\n")

    conf_agreement = analyze_confidence_with_disagreement(results)

    for agreement_level in ['low (<50%)', 'medium (50-80%)', 'high (80%+)']:
        if agreement_level in conf_agreement:
            print(f"\n{agreement_level} agreement:")
            for conf_level in ['<60%', '60-75%', '75%+']:
                if conf_level in conf_agreement[agreement_level]:
                    stats = conf_agreement[agreement_level][conf_level]
                    total = stats['wins'] + stats['losses']
                    if total >= 20:
                        rate = stats['wins'] / total * 100
                        print(f"  {conf_level} confidence: {rate:.1f}% ({stats['wins']}W/{stats['losses']}L)")

    # Summary
    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)

    print("""
Based on the analysis above, look for:

1. Agents with POSITIVE "Diff" in Analysis 1 - these provide contrarian value
   (better win rate when they disagree)

2. In Analysis 2, compare "Good Agree Bad Disagree" vs "Good Disagree Bad Agree"
   to see if filtering bad agent signals helps

3. Agents marked "CONTRARIAN" in Analysis 3 - when they disagree, bets win more

4. Agent pairs in Analysis 4 with high spread - indicates interaction effects

5. In Analysis 5, look for combinations where low agreement + high confidence
   outperforms high agreement + high confidence
""")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Analyze agent disagreement patterns')
    parser.add_argument('--weeks', '-w', type=str, default='11-16')
    args = parser.parse_args()

    if '-' in args.weeks:
        start, end = args.weeks.split('-')
        weeks = list(range(int(start), int(end) + 1))
    else:
        weeks = [int(w) for w in args.weeks.split(',')]

    print(f"Loading data for weeks {weeks}...")
    results = load_graded_results(weeks)

    if not results:
        print("No results found!")
        return 1

    print_analysis(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
