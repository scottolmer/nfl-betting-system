"""
Props Scorer - Score individual analyzed props (not just parlays)

Uses same CSV-based scoring logic as auto_scorer.py but scores ALL
analyzed props to provide comprehensive calibration data.
"""

from pathlib import Path
from typing import Dict, List
import auto_scorer
import prop_logger


def score_props_for_week(
    week: int,
    db_path: Path = None,
    data_dir: Path = None,
    dry_run: bool = True
) -> str:
    """
    Score all analyzed props for a given week.

    Args:
        week: NFL week number
        db_path: Path to SQLite database
        data_dir: Path to data directory with CSV files
        dry_run: If True, don't commit results to database

    Returns:
        Formatted string with scoring results
    """
    if db_path is None:
        db_path = Path(__file__).parent / "bets.db"

    if data_dir is None:
        data_dir = Path(__file__).parent / "data"

    # Load week stats (reuse from auto_scorer)
    week_stats = auto_scorer.load_week_stats(week, data_dir)

    if not week_stats:
        return f"\n[ERROR] No CSV files found for Week {week}\n"

    # Get all analyzed props for this week
    props = prop_logger.get_analyzed_props(week, db_path)

    if not props:
        return f"\n[INFO] No analyzed props found for Week {week}\n" \
               f"       Run 'analyze-week {week}' first to log props.\n"

    print(f"\n[INFO] Found {len(props)} analyzed props to score for Week {week}")

    # Score each prop
    results = {
        'total': len(props),
        'scored': 0,
        'hits': 0,
        'misses': 0,
        'unable_to_score': 0,
        'by_prop_type': {},
        'by_bet_type': {'OVER': {'total': 0, 'hits': 0}, 'UNDER': {'total': 0, 'hits': 0}},
        'by_confidence': {}
    }

    for prop in props:
        # Create a leg-like dictionary for scoring
        leg = {
            'player': prop['player'],
            'prop_type': prop['prop_type'],
            'bet_type': prop['bet_type'],
            'line': prop['line']
        }

        # Score using same logic as auto_scorer
        result, actual_value, debug_info = auto_scorer.score_leg(leg, week_stats)

        # Update prop in database (unless dry run)
        if not dry_run and result is not None:
            prop_logger.update_prop_results(prop['prop_id'], result, actual_value, db_path)

        # Collect statistics
        if result is not None:
            results['scored'] += 1

            if result == 1:
                results['hits'] += 1
            else:
                results['misses'] += 1

            # Track by prop type
            prop_type = prop['prop_type']
            if prop_type not in results['by_prop_type']:
                results['by_prop_type'][prop_type] = {'total': 0, 'hits': 0}
            results['by_prop_type'][prop_type]['total'] += 1
            if result == 1:
                results['by_prop_type'][prop_type]['hits'] += 1

            # Track by bet type
            bet_type = prop['bet_type']
            results['by_bet_type'][bet_type]['total'] += 1
            if result == 1:
                results['by_bet_type'][bet_type]['hits'] += 1

            # Track by confidence bucket
            conf_bucket = int(prop['confidence'] // 10) * 10
            if conf_bucket not in results['by_confidence']:
                results['by_confidence'][conf_bucket] = {'total': 0, 'hits': 0}
            results['by_confidence'][conf_bucket]['total'] += 1
            if result == 1:
                results['by_confidence'][conf_bucket]['hits'] += 1

        else:
            results['unable_to_score'] += 1

    # Format results
    return format_props_scoring_results(results, week, dry_run)


def format_props_scoring_results(results: Dict, week: int, dry_run: bool) -> str:
    """Format scoring results for display"""
    lines = []

    lines.append("\n" + "="*70)
    lines.append(f"PROPS SCORING RESULTS - WEEK {week} {'(DRY RUN)' if dry_run else ''}")
    lines.append("="*70)

    # Overall summary
    total = results['total']
    scored = results['scored']
    hits = results['hits']
    misses = results['misses']
    unable = results['unable_to_score']

    hit_rate = (hits / scored * 100) if scored > 0 else 0

    lines.append(f"\nOVERALL SUMMARY:")
    lines.append(f"  Total Props: {total}")
    lines.append(f"  Scored: {scored}")
    lines.append(f"  Hits: {hits} ({hit_rate:.1f}%)")
    lines.append(f"  Misses: {misses}")
    if unable > 0:
        lines.append(f"  Unable to Score: {unable} (player not in CSV)")

    # By prop type
    if results['by_prop_type']:
        lines.append(f"\nACCURACY BY PROP TYPE:")
        lines.append("-" * 70)
        for prop_type in sorted(results['by_prop_type'].keys()):
            stats = results['by_prop_type'][prop_type]
            prop_hit_rate = (stats['hits'] / stats['total'] * 100) if stats['total'] > 0 else 0
            lines.append(f"  {prop_type:20s}  {stats['hits']:3d}/{stats['total']:3d}  ({prop_hit_rate:5.1f}%)")

    # By bet type
    if results['by_bet_type']:
        lines.append(f"\nACCURACY BY BET TYPE:")
        lines.append("-" * 70)
        for bet_type in ['OVER', 'UNDER']:
            stats = results['by_bet_type'][bet_type]
            if stats['total'] > 0:
                bet_hit_rate = (stats['hits'] / stats['total'] * 100)
                lines.append(f"  {bet_type:20s}  {stats['hits']:3d}/{stats['total']:3d}  ({bet_hit_rate:5.1f}%)")

    # By confidence bucket
    if results['by_confidence']:
        lines.append(f"\nACCURACY BY CONFIDENCE:")
        lines.append("-" * 70)
        lines.append(f"  {'Confidence':20s}  {'Hits':>12s}  {'Hit Rate':>12s}  {'Calibration':>15s}")
        lines.append("-" * 70)

        for conf_bucket in sorted(results['by_confidence'].keys(), reverse=True):
            stats = results['by_confidence'][conf_bucket]
            bucket_hit_rate = (stats['hits'] / stats['total'] * 100) if stats['total'] > 0 else 0
            predicted_conf = conf_bucket + 5  # Mid-point of bucket
            calibration_error = bucket_hit_rate - predicted_conf

            error_str = f"{calibration_error:+.1f}pp"
            if abs(calibration_error) < 5:
                status = "[GOOD]"
            elif calibration_error < -10:
                status = "[OVERCONFIDENT]"
            else:
                status = "[UNDERCONFIDENT]"

            lines.append(
                f"  {conf_bucket}-{conf_bucket+9}%        "
                f"  {stats['hits']:3d}/{stats['total']:3d}    "
                f"{bucket_hit_rate:5.1f}%      "
                f"{error_str:>8s} {status}"
            )

    lines.append("\n" + "="*70)

    if dry_run:
        lines.append("[INFO] This was a dry run. Run without --dry-run to save results.")
    else:
        lines.append("[OK] Results saved to database!")

    lines.append("="*70 + "\n")

    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Score analyzed props from weekly CSV files')
    parser.add_argument('--week', type=int, required=True, help='NFL week number (1-18)')
    parser.add_argument('--dry-run', action='store_true', help='Preview scoring without saving')
    parser.add_argument('--db', type=str, help='Path to database file')
    parser.add_argument('--data-dir', type=str, help='Path to data directory')

    args = parser.parse_args()

    db_path = Path(args.db) if args.db else None
    data_dir = Path(args.data_dir) if args.data_dir else None

    output = score_props_for_week(
        week=args.week,
        db_path=db_path,
        data_dir=data_dir,
        dry_run=args.dry_run
    )

    print(output)
