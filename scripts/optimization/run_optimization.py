#!/usr/bin/env python
"""
Weight Optimization CLI

Run random search optimization to find optimal agent weights.

Usage:
    # Basic random search (100 samples)
    python scripts/optimization/run_optimization.py --samples 100

    # Larger search
    python scripts/optimization/run_optimization.py --samples 500 --weeks 11-16

    # Custom weight bounds
    python scripts/optimization/run_optimization.py --samples 200 --min-weight 0.1 --max-weight 4.0

    # Quick test run
    python scripts/optimization/run_optimization.py --samples 10 --weeks 11-12
"""

import sys
import argparse
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Direct imports to avoid circular import issues
from scripts.optimization.search_space import SearchSpace
from scripts.optimization.results_reporter import ResultsReporter

# Import weight_optimizer directly to avoid __init__.py chain
import importlib.util
spec = importlib.util.spec_from_file_location(
    "weight_optimizer",
    project_root / "scripts" / "optimization" / "weight_optimizer.py"
)
optimizer_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(optimizer_module)
WeightOptimizer = optimizer_module.WeightOptimizer


def parse_weeks(weeks_str: str) -> list:
    """
    Parse weeks argument.

    Args:
        weeks_str: String like "11-16" or "11,12,13"

    Returns:
        List of week numbers
    """
    if '-' in weeks_str:
        start, end = weeks_str.split('-')
        return list(range(int(start), int(end) + 1))
    else:
        return [int(w.strip()) for w in weeks_str.split(',')]


def main():
    parser = argparse.ArgumentParser(
        description='Run weight optimization using random search',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Basic optimization (100 samples):
    python scripts/optimization/run_optimization.py --samples 100

  Larger search with specific weeks:
    python scripts/optimization/run_optimization.py --samples 500 --weeks 11-16

  Custom weight bounds:
    python scripts/optimization/run_optimization.py --samples 200 --min-weight 0.5 --max-weight 3.0

  Quick test:
    python scripts/optimization/run_optimization.py --samples 10 --weeks 11-12
        """
    )

    parser.add_argument(
        '--samples', '-n',
        type=int,
        default=100,
        help='Number of random configurations to test (default: 100)'
    )

    parser.add_argument(
        '--weeks', '-w',
        type=str,
        default='11-16',
        help='Weeks to backtest, e.g. "11-16" or "11,12,13" (default: 11-16)'
    )

    parser.add_argument(
        '--min-confidence',
        type=int,
        default=50,
        help='Minimum confidence threshold for bets (default: 50)'
    )

    parser.add_argument(
        '--min-weight',
        type=float,
        default=None,
        help='Global minimum weight bound (default: use per-agent defaults)'
    )

    parser.add_argument(
        '--max-weight',
        type=float,
        default=None,
        help='Global maximum weight bound (default: use per-agent defaults)'
    )

    parser.add_argument(
        '--top', '-t',
        type=int,
        default=10,
        help='Number of top results to display (default: 10)'
    )

    parser.add_argument(
        '--save',
        action='store_true',
        help='Save results to JSON file'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Parse weeks
    weeks = parse_weeks(args.weeks)

    print(f"""
================================================================
         WEIGHT OPTIMIZATION - RANDOM SEARCH
================================================================

Configuration:
  Samples:        {args.samples}
  Weeks:          {weeks}
  Min Confidence: {args.min_confidence}
  Weight Range:   [{args.min_weight or 'default'}, {args.max_weight or 'default'}]
""")

    # Create search space
    search_space = SearchSpace(
        min_weight=args.min_weight,
        max_weight=args.max_weight
    )

    if args.verbose:
        print(search_space.describe())
        print()

    # Create optimizer
    optimizer = WeightOptimizer(
        weeks=weeks,
        min_confidence=args.min_confidence,
        search_space=search_space
    )

    # Run optimization
    results = optimizer.run_optimization(
        n_samples=args.samples,
        show_progress=not args.quiet
    )

    # Get baseline for comparison
    baseline = optimizer.get_baseline_result()

    # Report results
    reporter = ResultsReporter()
    reporter.print_results(results, baseline=baseline, top_n=args.top)

    # Print weight comparison table
    print(reporter.format_weights_table(results, top_n=min(5, args.top)))

    # Save results if requested
    if args.save and results:
        reporter.save_results_json(results)
        reporter.save_best_weights(results[0])

    # Return exit code based on improvement
    if baseline and results:
        improvement = results[0].win_rate - baseline.win_rate
        if improvement > 0:
            print(f"\n[OK] Found improved weights! (+{improvement:.1f}%)")
            return 0
        else:
            print(f"\n[!] No improvement over baseline found.")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
