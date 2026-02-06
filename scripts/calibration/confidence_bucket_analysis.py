#!/usr/bin/env python
"""
Confidence Bucket Analysis

Analyzes actual win rate by confidence bucket to determine
optimal confidence thresholds for parlay building.

Usage:
    python scripts/calibration/confidence_bucket_analysis.py
    python scripts/calibration/confidence_bucket_analysis.py --weeks 11-16
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

# Add project root to path
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
            print(f"  Loaded week {week}: {len(week_results)} predictions")
        else:
            print(f"  Week {week}: No graded results found")

    return all_results


def bucket_by_confidence(results: List[dict], bucket_size: int = 5) -> Dict[str, Dict]:
    """
    Bucket results by confidence score.

    Args:
        results: List of graded predictions
        bucket_size: Size of each bucket (default 5%)

    Returns:
        Dict mapping bucket range to stats
    """
    buckets = defaultdict(lambda: {'wins': 0, 'losses': 0, 'voids': 0, 'total': 0})

    for r in results:
        confidence = r.get('confidence', 0)
        result = r.get('result', '').upper()

        # Determine bucket
        bucket_start = (confidence // bucket_size) * bucket_size
        bucket_end = bucket_start + bucket_size
        bucket_key = f"{bucket_start}-{bucket_end}"

        buckets[bucket_key]['total'] += 1
        if result == 'WIN':
            buckets[bucket_key]['wins'] += 1
        elif result == 'LOSS':
            buckets[bucket_key]['losses'] += 1
        elif result in ('VOID', 'PUSH'):
            buckets[bucket_key]['voids'] += 1

    return dict(buckets)


def calculate_cumulative_stats(buckets: Dict[str, Dict]) -> List[Tuple[int, Dict]]:
    """
    Calculate cumulative stats for cutoff analysis.

    For each possible cutoff (50, 55, 60, etc.), calculate the win rate
    if you only bet on predictions >= that confidence.

    Returns:
        List of (cutoff, stats_dict) tuples
    """
    # Parse buckets into sorted order by starting confidence
    parsed = []
    for bucket_key, stats in buckets.items():
        start = int(bucket_key.split('-')[0])
        parsed.append((start, stats))

    parsed.sort(key=lambda x: x[0])

    # Calculate cumulative from highest to lowest
    cumulative_results = []

    # Get all unique starting points
    cutoffs = sorted(set(start for start, _ in parsed))

    for cutoff in cutoffs:
        # Sum stats for all buckets >= cutoff
        total_wins = 0
        total_losses = 0
        total_voids = 0
        total_bets = 0

        for start, stats in parsed:
            if start >= cutoff:
                total_wins += stats['wins']
                total_losses += stats['losses']
                total_voids += stats['voids']
                total_bets += stats['total']

        if total_bets > 0:
            decided = total_wins + total_losses
            win_rate = (total_wins / decided * 100) if decided > 0 else 0

            cumulative_results.append((cutoff, {
                'wins': total_wins,
                'losses': total_losses,
                'voids': total_voids,
                'total': total_bets,
                'decided': decided,
                'win_rate': win_rate
            }))

    return cumulative_results


def print_bucket_analysis(buckets: Dict[str, Dict]):
    """Print detailed bucket breakdown."""
    print("\n" + "=" * 70)
    print("CONFIDENCE BUCKET ANALYSIS")
    print("=" * 70)
    print("\nActual Win Rate by Confidence Bucket:")
    print("-" * 70)
    print(f"{'Bucket':>12s}  {'Wins':>6s}  {'Losses':>6s}  {'Voids':>6s}  {'Total':>6s}  {'Win Rate':>10s}")
    print("-" * 70)

    # Sort buckets by starting confidence
    sorted_buckets = sorted(
        buckets.items(),
        key=lambda x: int(x[0].split('-')[0])
    )

    for bucket_key, stats in sorted_buckets:
        decided = stats['wins'] + stats['losses']
        win_rate = (stats['wins'] / decided * 100) if decided > 0 else 0

        print(f"{bucket_key:>12s}  {stats['wins']:>6d}  {stats['losses']:>6d}  "
              f"{stats['voids']:>6d}  {stats['total']:>6d}  {win_rate:>9.1f}%")

    print("-" * 70)


def print_cutoff_analysis(cumulative: List[Tuple[int, Dict]]):
    """Print cutoff analysis for parlay building."""
    print("\n" + "=" * 70)
    print("CONFIDENCE CUTOFF ANALYSIS (for parlay building)")
    print("=" * 70)
    print("\nIf you only bet on predictions >= cutoff:")
    print("-" * 70)
    print(f"{'Cutoff':>8s}  {'Wins':>6s}  {'Losses':>6s}  {'Total':>6s}  {'Win Rate':>10s}  {'Note':>20s}")
    print("-" * 70)

    best_rate = 0
    best_cutoff = 50

    for cutoff, stats in cumulative:
        note = ""
        if stats['win_rate'] > best_rate and stats['decided'] >= 20:
            best_rate = stats['win_rate']
            best_cutoff = cutoff
            note = "<-- Best so far"
        elif stats['decided'] < 20:
            note = "(small sample)"

        print(f"{cutoff:>7d}%  {stats['wins']:>6d}  {stats['losses']:>6d}  "
              f"{stats['decided']:>6d}  {stats['win_rate']:>9.1f}%  {note:>20s}")

    print("-" * 70)

    return best_cutoff, best_rate


def print_recommendations(cumulative: List[Tuple[int, Dict]], best_cutoff: int, best_rate: float):
    """Print recommendations for parlay building."""
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS FOR PARLAY BUILDING")
    print("=" * 70)

    # Find stats at different key thresholds
    thresholds = {50: None, 60: None, 70: None, 75: None, 80: None}
    for cutoff, stats in cumulative:
        if cutoff in thresholds:
            thresholds[cutoff] = stats

    print("\nKey thresholds comparison:")
    print("-" * 70)

    for threshold, stats in thresholds.items():
        if stats and stats['decided'] >= 10:
            print(f"  >= {threshold}%: {stats['win_rate']:.1f}% win rate ({stats['wins']}W/{stats['losses']}L)")

    print(f"\nOptimal cutoff (with adequate sample): >= {best_cutoff}%")
    print(f"  Expected win rate: {best_rate:.1f}%")

    # Calculate break-even for parlays
    print("\nParlay math (assuming -110 odds):")
    print("-" * 70)

    # For 2-leg, 3-leg, 4-leg parlays, show expected hit rates needed
    parlay_legs = [2, 3, 4, 5]
    for legs in parlay_legs:
        # If individual leg win rate is p, parlay hit rate is p^legs
        # Break-even for n-leg parlay at -110 individual odds is approximately:
        # Payout = 2.64^legs for 2-leg, increases with legs
        # We need: hit_rate * payout > 1

        # Standard payouts (approximate)
        payouts = {2: 2.64, 3: 6.0, 4: 12.3, 5: 24.3}
        payout = payouts.get(legs, 2.64 ** legs)
        breakeven = 1 / payout

        # Expected hit rate at best cutoff
        if thresholds.get(best_cutoff):
            expected_rate = (best_rate / 100) ** legs
            ev = (expected_rate * payout) - 1
            ev_str = f"+{ev*100:.1f}%" if ev > 0 else f"{ev*100:.1f}%"
            print(f"  {legs}-leg parlay: Need {breakeven*100:.1f}% hit rate, "
                  f"expected {expected_rate*100:.1f}% at {best_cutoff}%+ cutoff (EV: {ev_str})")

    print("\n" + "=" * 70)


def parse_weeks(weeks_str: str) -> List[int]:
    """Parse weeks argument."""
    if '-' in weeks_str:
        start, end = weeks_str.split('-')
        return list(range(int(start), int(end) + 1))
    else:
        return [int(w.strip()) for w in weeks_str.split(',')]


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Analyze win rate by confidence bucket')
    parser.add_argument('--weeks', '-w', type=str, default='11-16',
                       help='Weeks to analyze (default: 11-16)')
    parser.add_argument('--bucket-size', '-b', type=int, default=5,
                       help='Confidence bucket size (default: 5)')

    args = parser.parse_args()
    weeks = parse_weeks(args.weeks)

    print(f"\nLoading graded results for weeks {weeks}...")
    results = load_graded_results(weeks)

    if not results:
        print("No graded results found!")
        return 1

    print(f"\nTotal predictions: {len(results)}")

    # Bucket analysis
    buckets = bucket_by_confidence(results, args.bucket_size)
    print_bucket_analysis(buckets)

    # Cutoff analysis
    cumulative = calculate_cumulative_stats(buckets)
    best_cutoff, best_rate = print_cutoff_analysis(cumulative)

    # Recommendations
    print_recommendations(cumulative, best_cutoff, best_rate)

    return 0


if __name__ == "__main__":
    sys.exit(main())
