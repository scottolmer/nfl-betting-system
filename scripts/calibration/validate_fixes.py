#!/usr/bin/env python
"""
Validate Calibration Fixes

Runs backtest with and without calibration to measure improvement.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.backtesting.backtest_engine import BacktestEngine
from scripts.optimization.in_memory_grader import InMemoryGrader


def run_validation(weeks=[11, 12, 13, 14, 15, 16], min_confidence=50):
    """Compare performance with vs without calibration."""

    print("=" * 70)
    print("CALIBRATION FIX VALIDATION")
    print("=" * 70)
    print(f"\nWeeks: {weeks}")
    print(f"Min confidence: {min_confidence}")

    # Initialize grader
    grader = InMemoryGrader()
    grader.preload_weeks(weeks)

    # Test 1: Run WITH calibration (new default)
    print("\n" + "-" * 70)
    print("TEST 1: WITH calibration fixes (new defaults)")
    print("-" * 70)

    # Use new calibrated weights
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

    engine_calibrated = BacktestEngine(custom_weights=calibrated_weights)

    total_wins_cal = 0
    total_losses_cal = 0
    total_voids_cal = 0

    for week in weeks:
        predictions = engine_calibrated.run_backtest_in_memory(week, min_confidence)
        wins, losses, voids = grader.grade_predictions(predictions, week)
        total_wins_cal += wins
        total_losses_cal += losses
        total_voids_cal += voids
        decided = wins + losses
        rate = wins / decided * 100 if decided > 0 else 0
        print(f"  Week {week}: {wins}W/{losses}L ({rate:.1f}%)")

    decided_cal = total_wins_cal + total_losses_cal
    rate_cal = total_wins_cal / decided_cal * 100 if decided_cal > 0 else 0
    print(f"\nCalibrated Total: {total_wins_cal}W/{total_losses_cal}L = {rate_cal:.1f}%")

    # Test 2: Run WITHOUT calibration (old weights)
    print("\n" + "-" * 70)
    print("TEST 2: WITHOUT calibration (old defaults)")
    print("-" * 70)

    old_weights = {
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

    engine_old = BacktestEngine(custom_weights=old_weights)

    total_wins_old = 0
    total_losses_old = 0
    total_voids_old = 0

    for week in weeks:
        predictions = engine_old.run_backtest_in_memory(week, min_confidence)
        wins, losses, voids = grader.grade_predictions(predictions, week)
        total_wins_old += wins
        total_losses_old += losses
        total_voids_old += voids
        decided = wins + losses
        rate = wins / decided * 100 if decided > 0 else 0
        print(f"  Week {week}: {wins}W/{losses}L ({rate:.1f}%)")

    decided_old = total_wins_old + total_losses_old
    rate_old = total_wins_old / decided_old * 100 if decided_old > 0 else 0
    print(f"\nOld Total: {total_wins_old}W/{total_losses_old}L = {rate_old:.1f}%")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    improvement = rate_cal - rate_old
    print(f"\nOld weights:        {rate_old:.1f}% ({total_wins_old}W/{total_losses_old}L)")
    print(f"Calibrated weights: {rate_cal:.1f}% ({total_wins_cal}W/{total_losses_cal}L)")
    print(f"Improvement:        {improvement:+.1f}%")

    if improvement > 0:
        print("\n[OK] Calibration fixes improved performance!")
    elif improvement < 0:
        print("\n[!!] Calibration fixes hurt performance - review needed")
    else:
        print("\n[--] No change in performance")

    print("=" * 70)

    return improvement


if __name__ == "__main__":
    run_validation()
