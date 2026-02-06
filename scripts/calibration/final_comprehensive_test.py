#!/usr/bin/env python
"""
Final Comprehensive Test

Compares the original baseline system to the fully calibrated system
to measure total improvement from all offseason optimizations.

Original Baseline:
- 9 agents (DVOA, Matchup, Volume, Injury, Trend, GameScript, Variance, Weather, HitRate)
- Original weights (DVOA: 2.0, Matchup: 1.5, etc.)
- No calibration fixes

Fully Calibrated:
- 6 agents (removed HitRate, Weather, Trend)
- Optimized weights
- Anti-predictive agent inversion (Variance, GameScript)
- Agreement penalty/bonus
- Stat type bonuses
- Over/under bias correction
- Excluded stat types (player_tds_over)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def load_graded_results(weeks):
    """Load graded results for validation."""
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


def grade_predictions(predictions, graded_results, week):
    """Grade predictions against actual results."""
    # Build lookup from graded results
    actuals = {}
    for r in graded_results:
        if r.get('week') != week:
            continue
        key = (
            r.get('player_name', '').lower(),
            r.get('stat_type', ''),
            r.get('line'),
            r.get('bet_type', '').upper()
        )
        actuals[key] = r.get('result', '').upper()

    wins = losses = voids = 0
    for p in predictions:
        key = (
            p.get('player_name', '').lower(),
            p.get('stat_type', ''),
            p.get('line'),
            p.get('bet_type', '').upper()
        )
        result = actuals.get(key)
        if result == 'WIN':
            wins += 1
        elif result == 'LOSS':
            losses += 1
        else:
            voids += 1

    return wins, losses, voids


def run_original_baseline(weeks, min_confidence, graded_results):
    """Run with original 9-agent system and old weights."""
    print("\n" + "=" * 70)
    print("ORIGINAL BASELINE (Pre-Optimization)")
    print("=" * 70)
    print("Config: 9 agents, original weights, no calibration")
    print("-" * 70)

    # Original weights
    original_weights = {
        'DVOA': 2.0,
        'Matchup': 1.5,
        'Volume': 1.5,
        'Injury': 3.0,
        'Trend': 1.0,
        'GameScript': 2.2,
        'Variance': 1.2,
        'Weather': 1.3,
        'HitRate': 2.0,
    }

    from scripts.analysis.data_loader import NFLDataLoader

    # We need to use the old orchestrator behavior
    # Since we've modified the orchestrator, we'll simulate by using
    # apply_calibration=False and manually adding back the removed agents
    # Actually, we can't easily do this since agents are removed from code

    # Instead, let's use the graded results directly to calculate what
    # the baseline performance was (since those were graded with old system)

    # Filter graded results by confidence threshold
    total_wins = 0
    total_losses = 0
    total_voids = 0

    for week in weeks:
        week_wins = 0
        week_losses = 0
        week_voids = 0
        week_count = 0

        for r in graded_results:
            if r.get('week') != week:
                continue

            confidence = r.get('confidence', 0)
            if confidence < min_confidence:
                continue

            result = r.get('result', '').upper()
            week_count += 1

            if result == 'WIN':
                week_wins += 1
            elif result == 'LOSS':
                week_losses += 1
            else:
                week_voids += 1

        total_wins += week_wins
        total_losses += week_losses
        total_voids += week_voids

        decided = week_wins + week_losses
        rate = week_wins / decided * 100 if decided > 0 else 0
        print(f"  Week {week}: {week_wins}W/{week_losses}L ({rate:.1f}%) - {week_count} predictions")

    decided = total_wins + total_losses
    rate = total_wins / decided * 100 if decided > 0 else 0

    print("-" * 70)
    print(f"BASELINE TOTAL: {total_wins}W/{total_losses}L = {rate:.1f}%")
    print(f"Total bets: {decided}")

    return total_wins, total_losses, decided, rate


def run_calibrated_system(weeks, min_confidence):
    """Run with fully calibrated 6-agent system."""
    print("\n" + "=" * 70)
    print("FULLY CALIBRATED SYSTEM (Post-Optimization)")
    print("=" * 70)
    print("Config: 6 agents, optimized weights, all calibration fixes")
    print("  - Removed: HitRate, Weather, Trend")
    print("  - Inverted: Variance, GameScript")
    print("  - Agreement penalty/bonus enabled")
    print("  - Stat type bonuses enabled")
    print("  - Over/under bias correction enabled")
    print("-" * 70)

    from scripts.analysis.data_loader import NFLDataLoader
    from scripts.analysis.orchestrator import PropAnalyzer
    from scripts.optimization.in_memory_grader import InMemoryGrader

    # Calibrated weights
    calibrated_weights = {
        'DVOA': 3.2,
        'Matchup': 0.5,
        'Volume': 0.75,
        'Injury': 4.7,
        'GameScript': 0.82,
        'Variance': 2.4,
    }

    grader = InMemoryGrader()
    grader.preload_weeks(weeks)

    total_wins = 0
    total_losses = 0
    total_voids = 0
    total_predictions = 0

    for week in weeks:
        loader = NFLDataLoader(data_dir=str(project_root / "data"))
        context = loader.load_all_data(week=week)

        if not context.get('props'):
            print(f"  Week {week}: No props data")
            continue

        # Create analyzer with full calibration
        analyzer = PropAnalyzer(custom_weights=calibrated_weights, apply_calibration=True)
        all_analyses = analyzer.analyze_all_props(context, min_confidence=min_confidence)

        predictions = []
        for analysis in all_analyses:
            predictions.append({
                'player_name': analysis.prop.player_name,
                'team': analysis.prop.team,
                'opponent': analysis.prop.opponent,
                'stat_type': analysis.prop.stat_type,
                'line': analysis.prop.line,
                'bet_type': analysis.prop.bet_type,
                'confidence': analysis.final_confidence,
            })

        wins, losses, voids = grader.grade_predictions(predictions, week)
        total_wins += wins
        total_losses += losses
        total_voids += voids
        total_predictions += len(predictions)

        decided = wins + losses
        rate = wins / decided * 100 if decided > 0 else 0
        print(f"  Week {week}: {wins}W/{losses}L ({rate:.1f}%) - {len(predictions)} predictions")

    decided = total_wins + total_losses
    rate = total_wins / decided * 100 if decided > 0 else 0

    print("-" * 70)
    print(f"CALIBRATED TOTAL: {total_wins}W/{total_losses}L = {rate:.1f}%")
    print(f"Total bets: {decided}")

    return total_wins, total_losses, decided, rate


def print_final_summary(baseline_stats, calibrated_stats):
    """Print final comparison summary."""
    b_wins, b_losses, b_total, b_rate = baseline_stats
    c_wins, c_losses, c_total, c_rate = calibrated_stats

    improvement = c_rate - b_rate
    volume_change = c_total - b_total

    print("\n")
    print("=" * 70)
    print("                    FINAL RESULTS SUMMARY")
    print("=" * 70)
    print(f"""
+---------------------------+------------------+------------------+
|                           |     BASELINE     |    CALIBRATED    |
+---------------------------+------------------+------------------+
| Agents                    |        9         |        6         |
| Win Rate                  |     {b_rate:>5.1f}%       |     {c_rate:>5.1f}%       |
| Record                    | {b_wins:>5d}W/{b_losses:<5d}L   | {c_wins:>5d}W/{c_losses:<5d}L   |
| Total Bets                |     {b_total:>5d}        |     {c_total:>5d}        |
+---------------------------+------------------+------------------+
| IMPROVEMENT               |            {improvement:>+5.1f}%              |
| Volume Change             |            {volume_change:>+5d} bets           |
+---------------------------+------------------+------------------+
""")

    print("CALIBRATION CHANGES APPLIED:")
    print("-" * 70)
    print("""
  1. AGENTS REMOVED (no predictive value):
     - HitRate: 51% accuracy both directions (coin flip)
     - Weather: No data available
     - Trend: 68% neutral, rarely signaled

  2. AGENTS INVERTED (contrarian value):
     - Variance: 35% -> 60% when inverted
     - GameScript: 36% -> 60% when inverted

  3. WEIGHT OPTIMIZATION:
     - Injury: 3.0 -> 4.7 (highly predictive)
     - DVOA: 2.0 -> 3.2 (valuable signal)
     - Matchup: 1.5 -> 0.5 (was hurting predictions)
     - Volume: 1.5 -> 0.75 (was hurting predictions)

  4. CALIBRATION FIXES:
     - Agreement penalty: -12 when >80% agents agree
     - Disagreement bonus: +8 when <50% agents agree
     - Over/under bias correction by stat type
     - Stat type bonuses for high-reliability props
     - Excluded player_tds_over (0% win rate)
""")

    print("=" * 70)

    # ROI calculation assuming -110 odds
    baseline_roi = (b_rate / 100 * 1.91) - 1
    calibrated_roi = (c_rate / 100 * 1.91) - 1

    print(f"\nESTIMATED ROI (assuming -110 odds):")
    print(f"  Baseline:   {baseline_roi*100:>+5.1f}%")
    print(f"  Calibrated: {calibrated_roi*100:>+5.1f}%")
    print(f"  Improvement: {(calibrated_roi - baseline_roi)*100:>+5.1f}%")

    print("\n" + "=" * 70)
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


def main():
    weeks = [11, 12, 13, 14, 15, 16]
    min_confidence = 50

    print("=" * 70)
    print("       FINAL COMPREHENSIVE TEST: BASELINE vs CALIBRATED")
    print("=" * 70)
    print(f"\nTest Parameters:")
    print(f"  Weeks: {weeks}")
    print(f"  Min Confidence: {min_confidence}")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load graded results for baseline calculation
    print("\nLoading graded results...")
    graded_results = load_graded_results(weeks)
    print(f"Loaded {len(graded_results)} graded predictions")

    # Run baseline (using historical graded data)
    baseline_stats = run_original_baseline(weeks, min_confidence, graded_results)

    # Run calibrated system
    calibrated_stats = run_calibrated_system(weeks, min_confidence)

    # Print summary
    print_final_summary(baseline_stats, calibrated_stats)


if __name__ == "__main__":
    main()
