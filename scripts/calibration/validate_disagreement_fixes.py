#!/usr/bin/env python
"""
Validate Disagreement Fixes

Compares performance with and without the new calibration fixes:
1. Anti-predictive agent inversion (Trend, Variance, GameScript)
2. Agreement penalty/bonus
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.backtesting.backtest_engine import BacktestEngine
from scripts.optimization.in_memory_grader import InMemoryGrader


def run_validation(weeks=[11, 12, 13, 14, 15, 16], min_confidence=50):
    """Compare performance with vs without new calibration fixes."""

    print("=" * 70)
    print("DISAGREEMENT FIX VALIDATION")
    print("=" * 70)
    print(f"\nWeeks: {weeks}")
    print(f"Min confidence: {min_confidence}")
    print("\nFixes being tested:")
    print("  1. Anti-predictive agent inversion (Trend, Variance, GameScript)")
    print("  2. Agreement penalty (high agreement = reduce confidence)")
    print("  3. Disagreement bonus (low agreement = boost confidence)")

    # Initialize grader
    grader = InMemoryGrader()
    grader.preload_weeks(weeks)

    # Use calibrated weights for both tests
    calibrated_weights = {
        'DVOA': 3.2,
        'Matchup': 0.5,
        'Volume': 0.75,
        'Injury': 4.7,
        'Trend': 0.67,
        'GameScript': 0.82,
        'Variance': 2.4,
        'Weather': 0.42,
        'HitRate': 1.0,
    }

    # Test 1: WITH new fixes (apply_calibration=True is default)
    print("\n" + "-" * 70)
    print("TEST 1: WITH disagreement fixes (new)")
    print("-" * 70)

    engine_new = BacktestEngine(custom_weights=calibrated_weights)

    total_wins_new = 0
    total_losses_new = 0

    for week in weeks:
        predictions = engine_new.run_backtest_in_memory(week, min_confidence)
        wins, losses, voids = grader.grade_predictions(predictions, week)
        total_wins_new += wins
        total_losses_new += losses
        decided = wins + losses
        rate = wins / decided * 100 if decided > 0 else 0
        print(f"  Week {week}: {wins}W/{losses}L ({rate:.1f}%) - {len(predictions)} predictions")

    decided_new = total_wins_new + total_losses_new
    rate_new = total_wins_new / decided_new * 100 if decided_new > 0 else 0
    print(f"\nNew Total: {total_wins_new}W/{total_losses_new}L = {rate_new:.1f}%")

    # Test 2: WITHOUT new fixes (disable calibration)
    print("\n" + "-" * 70)
    print("TEST 2: WITHOUT disagreement fixes (calibration disabled)")
    print("-" * 70)

    # Need to temporarily modify the PropAnalyzer to disable calibration
    # We'll do this by creating a new engine with apply_calibration=False
    from scripts.analysis.orchestrator import PropAnalyzer
    from scripts.analysis.data_loader import NFLDataLoader

    total_wins_old = 0
    total_losses_old = 0

    for week in weeks:
        loader = NFLDataLoader(data_dir=str(project_root / "data"))
        context = loader.load_all_data(week=week)

        if not context.get('props'):
            print(f"  Week {week}: No props data")
            continue

        # Create analyzer with calibration DISABLED
        analyzer = PropAnalyzer(custom_weights=calibrated_weights, apply_calibration=False)
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
        total_wins_old += wins
        total_losses_old += losses
        decided = wins + losses
        rate = wins / decided * 100 if decided > 0 else 0
        print(f"  Week {week}: {wins}W/{losses}L ({rate:.1f}%) - {len(predictions)} predictions")

    decided_old = total_wins_old + total_losses_old
    rate_old = total_wins_old / decided_old * 100 if decided_old > 0 else 0
    print(f"\nOld Total: {total_wins_old}W/{total_losses_old}L = {rate_old:.1f}%")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    improvement = rate_new - rate_old
    print(f"\nWithout disagreement fixes: {rate_old:.1f}% ({total_wins_old}W/{total_losses_old}L)")
    print(f"With disagreement fixes:    {rate_new:.1f}% ({total_wins_new}W/{total_losses_new}L)")
    print(f"Improvement:                {improvement:+.1f}%")

    # Also show bet volume change
    volume_change = decided_new - decided_old
    print(f"\nBet volume change: {volume_change:+d} bets")

    if improvement > 0:
        print("\n[SUCCESS] Disagreement fixes improved performance!")
    elif improvement < 0:
        print("\n[WARNING] Disagreement fixes hurt performance - review needed")
    else:
        print("\n[NEUTRAL] No change in performance")

    print("=" * 70)

    return improvement


if __name__ == "__main__":
    run_validation()
