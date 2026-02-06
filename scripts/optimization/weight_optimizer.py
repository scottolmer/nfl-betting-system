"""
Weight Optimizer - Main Optimization Engine

Runs the backtester multiple times with different weight configurations
to find optimal agent weights using random search.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Direct imports to avoid circular import issues via __init__.py files
from scripts.optimization.search_space import SearchSpace
from scripts.optimization.in_memory_grader import InMemoryGrader

# Import BacktestEngine directly from the module file to avoid __init__ chain
import importlib.util
spec = importlib.util.spec_from_file_location(
    "backtest_engine",
    project_root / "scripts" / "backtesting" / "backtest_engine.py"
)
backtest_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backtest_module)
BacktestEngine = backtest_module.BacktestEngine

# Suppress verbose logging during optimization
logging.getLogger('scripts.analysis').setLevel(logging.WARNING)
logging.getLogger('scripts.backtesting').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of evaluating a single weight configuration."""
    weights: Dict[str, float]
    wins: int
    losses: int
    voids: int
    total_bets: int
    win_rate: float
    weeks_evaluated: List[int]


class WeightOptimizer:
    """
    Main optimization engine for finding optimal agent weights.

    Uses random search to explore the weight space, evaluating each
    configuration by running backtests across multiple weeks and
    grading the results.
    """

    def __init__(self,
                 data_dir=None,
                 weeks: List[int] = None,
                 min_confidence: int = 50,
                 search_space: SearchSpace = None):
        """
        Initialize the optimizer.

        Args:
            data_dir: Path to data directory
            weeks: List of weeks to backtest (default: 11-16)
            min_confidence: Minimum confidence threshold for bets
            search_space: SearchSpace instance (default: creates new one)
        """
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = data_dir or (self.project_root / "data")
        self.weeks = weeks or list(range(11, 17))  # Weeks 11-16 by default
        self.min_confidence = min_confidence
        self.search_space = search_space or SearchSpace()

        # Initialize grader and preload stats
        self.grader = InMemoryGrader(data_dir=self.data_dir)
        logger.info(f"Pre-loading stats for weeks {self.weeks}...")
        self.grader.preload_weeks(self.weeks)

        # Store results
        self.results: List[OptimizationResult] = []

    def evaluate_weights(self, weights: Dict[str, float]) -> OptimizationResult:
        """
        Evaluate a single weight configuration.

        Runs backtest across all weeks with the given weights and grades results.

        Args:
            weights: Dict mapping agent names to weights

        Returns:
            OptimizationResult with win/loss stats
        """
        total_wins = 0
        total_losses = 0
        total_voids = 0

        engine = BacktestEngine(data_dir=self.data_dir, custom_weights=weights)

        for week in self.weeks:
            try:
                # Run backtest in memory
                predictions = engine.run_backtest_in_memory(week, min_confidence=self.min_confidence)

                if not predictions:
                    continue

                # Grade predictions
                wins, losses, voids = self.grader.grade_predictions(predictions, week)
                total_wins += wins
                total_losses += losses
                total_voids += voids

            except Exception as e:
                logger.debug(f"Error evaluating week {week}: {e}")
                continue

        total_bets = total_wins + total_losses
        win_rate = (total_wins / total_bets * 100) if total_bets > 0 else 0.0

        return OptimizationResult(
            weights=weights,
            wins=total_wins,
            losses=total_losses,
            voids=total_voids,
            total_bets=total_bets,
            win_rate=win_rate,
            weeks_evaluated=self.weeks
        )

    def run_optimization(self, n_samples: int = 100, show_progress: bool = True) -> List[OptimizationResult]:
        """
        Run random search optimization.

        Args:
            n_samples: Number of random configurations to evaluate
            show_progress: If True, shows progress bar

        Returns:
            List of OptimizationResult sorted by win_rate descending
        """
        self.results = []

        # Generate random configurations (includes baseline as first)
        configs = self.search_space.generate_random_configurations(n_samples, include_default=True)

        logger.info(f"Running optimization with {len(configs)} configurations...")
        logger.info(f"Weeks: {self.weeks}, Min confidence: {self.min_confidence}")

        start_time = time.time()

        for i, weights in enumerate(configs):
            if show_progress:
                progress = (i + 1) / len(configs) * 100
                elapsed = time.time() - start_time
                eta = (elapsed / (i + 1)) * (len(configs) - i - 1) if i > 0 else 0
                print(f"\rProgress: {i+1}/{len(configs)} ({progress:.1f}%) - ETA: {eta:.0f}s", end="", flush=True)

            result = self.evaluate_weights(weights)
            self.results.append(result)

            # Mark baseline
            if i == 0:
                logger.debug(f"Baseline: {result.win_rate:.1f}% ({result.wins}W/{result.losses}L)")

        if show_progress:
            print()  # Newline after progress

        elapsed_total = time.time() - start_time
        logger.info(f"Optimization completed in {elapsed_total:.1f}s")

        # Sort by win rate descending
        self.results.sort(key=lambda r: r.win_rate, reverse=True)

        return self.results

    def get_top_results(self, n: int = 10) -> List[OptimizationResult]:
        """
        Get top N results by win rate.

        Args:
            n: Number of top results to return

        Returns:
            List of top N OptimizationResult
        """
        if not self.results:
            return []
        return self.results[:n]

    def get_baseline_result(self) -> Optional[OptimizationResult]:
        """
        Get the baseline (default weights) result.

        Returns:
            OptimizationResult for baseline weights, or None if not run
        """
        baseline_weights = self.search_space.get_default_weights()

        for result in self.results:
            if result.weights == baseline_weights:
                return result

        return None


if __name__ == "__main__":
    # Demo: Run small optimization
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    optimizer = WeightOptimizer(weeks=[11, 12])
    results = optimizer.run_optimization(n_samples=10)

    print("\nTop 3 Results:")
    for i, r in enumerate(optimizer.get_top_results(3)):
        print(f"\n#{i+1} - Win Rate: {r.win_rate:.1f}% ({r.wins}W/{r.losses}L)")
        for name, weight in sorted(r.weights.items()):
            print(f"  {name}: {weight:.2f}")
