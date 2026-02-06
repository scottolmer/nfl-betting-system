"""
Results Reporter for Weight Optimization

Formats and saves optimization results, compares to baseline,
and provides analysis of top configurations.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.optimization.search_space import SearchSpace


# Define OptimizationResult here to avoid circular import
# This matches the definition in weight_optimizer.py
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


class ResultsReporter:
    """
    Formats and reports optimization results.
    """

    def __init__(self, output_dir: Path = None):
        """
        Initialize the reporter.

        Args:
            output_dir: Directory to save results (default: data/optimization_results)
        """
        self.project_root = Path(__file__).parent.parent.parent
        self.output_dir = output_dir or (self.project_root / "data" / "optimization_results")
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def print_results(self,
                      results: List[OptimizationResult],
                      baseline: Optional[OptimizationResult] = None,
                      top_n: int = 10):
        """
        Print formatted optimization results to console.

        Args:
            results: List of OptimizationResult sorted by win_rate
            baseline: Baseline result for comparison
            top_n: Number of top results to show
        """
        print("\n" + "=" * 60)
        print(f"WEIGHT OPTIMIZATION RESULTS ({len(results)} samples)")
        print("=" * 60)

        if baseline:
            print(f"\nBaseline (current weights): {baseline.win_rate:.1f}% "
                  f"({baseline.wins}W/{baseline.losses}L)")
            print("-" * 60)

        print(f"\nTOP {min(top_n, len(results))} CONFIGURATIONS:")
        print("-" * 60)

        for i, r in enumerate(results[:top_n]):
            # Check if this is the baseline
            is_baseline = baseline and r.weights == baseline.weights
            baseline_marker = " (BASELINE)" if is_baseline else ""

            print(f"\n#{i+1} - Win Rate: {r.win_rate:.1f}% ({r.wins}W/{r.losses}L){baseline_marker}")

            # Format weights in a single line
            weight_strs = [f"{name}: {weight:.2f}" for name, weight in sorted(r.weights.items())]
            print(f"   {', '.join(weight_strs)}")

        # Show improvement if baseline available
        if baseline and results:
            best = results[0]
            improvement = best.win_rate - baseline.win_rate
            print("\n" + "-" * 60)
            print(f"Baseline: {baseline.win_rate:.1f}%")
            print(f"Best found: {best.win_rate:.1f}%")
            if improvement > 0:
                print(f"Improvement: +{improvement:.1f}%")
            elif improvement < 0:
                print(f"Change: {improvement:.1f}% (baseline is optimal)")
            else:
                print("No improvement over baseline")
        print("=" * 60)

    def format_weights_table(self, results: List[OptimizationResult], top_n: int = 5) -> str:
        """
        Create a formatted table comparing top weight configurations.

        Args:
            results: List of OptimizationResult
            top_n: Number of configs to compare

        Returns:
            Formatted string table
        """
        if not results:
            return "No results to display"

        search_space = SearchSpace()
        agent_names = search_space.get_agent_names()

        lines = []
        lines.append("\nWeight Comparison Table:")
        lines.append("-" * 80)

        # Header
        header = f"{'Agent':12s}"
        for i in range(min(top_n, len(results))):
            header += f"  #{i+1:>5d}"
        lines.append(header)
        lines.append("-" * 80)

        # Each agent row
        for agent in agent_names:
            row = f"{agent:12s}"
            for r in results[:top_n]:
                row += f"  {r.weights.get(agent, 0):>6.2f}"
            lines.append(row)

        lines.append("-" * 80)

        # Win rate row
        row = f"{'Win Rate':12s}"
        for r in results[:top_n]:
            row += f"  {r.win_rate:>5.1f}%"
        lines.append(row)

        return "\n".join(lines)

    def save_results_json(self, results: List[OptimizationResult], filename: str = None) -> Path:
        """
        Save all results to JSON file.

        Args:
            results: List of OptimizationResult
            filename: Optional filename (default: auto-generated with timestamp)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"optimization_results_{timestamp}.json"

        output_path = self.output_dir / filename

        # Convert results to JSON-serializable format
        json_results = []
        for r in results:
            json_results.append({
                'weights': r.weights,
                'wins': r.wins,
                'losses': r.losses,
                'voids': r.voids,
                'total_bets': r.total_bets,
                'win_rate': round(r.win_rate, 2),
                'weeks_evaluated': r.weeks_evaluated
            })

        output_data = {
            'timestamp': datetime.now().isoformat(),
            'total_samples': len(results),
            'results': json_results
        }

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\nResults saved to: {output_path}")
        return output_path

    def save_best_weights(self, result: OptimizationResult, filename: str = "best_weights.json") -> Path:
        """
        Save the best weight configuration separately.

        Args:
            result: The best OptimizationResult
            filename: Output filename

        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename

        output_data = {
            'timestamp': datetime.now().isoformat(),
            'win_rate': round(result.win_rate, 2),
            'record': f"{result.wins}W/{result.losses}L",
            'weeks_evaluated': result.weeks_evaluated,
            'weights': result.weights
        }

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"Best weights saved to: {output_path}")
        return output_path

    def generate_report(self,
                        results: List[OptimizationResult],
                        baseline: Optional[OptimizationResult] = None) -> str:
        """
        Generate a full text report.

        Args:
            results: List of OptimizationResult
            baseline: Baseline result

        Returns:
            Full report as string
        """
        lines = []
        lines.append("WEIGHT OPTIMIZATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total configurations tested: {len(results)}")

        if results:
            lines.append(f"Weeks evaluated: {results[0].weeks_evaluated}")
            lines.append("")

            if baseline:
                lines.append("BASELINE PERFORMANCE:")
                lines.append(f"  Win Rate: {baseline.win_rate:.1f}% ({baseline.wins}W/{baseline.losses}L)")
                lines.append("")

            lines.append("TOP 10 CONFIGURATIONS:")
            lines.append("-" * 60)

            for i, r in enumerate(results[:10]):
                lines.append(f"\n#{i+1} Win Rate: {r.win_rate:.1f}% ({r.wins}W/{r.losses}L)")
                for name, weight in sorted(r.weights.items()):
                    default = SearchSpace.DEFAULT_RANGES[name].default
                    diff = weight - default
                    diff_str = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"
                    lines.append(f"  {name:12s}: {weight:.2f} ({diff_str} from default)")

            lines.append("")
            lines.append(self.format_weights_table(results))

            if baseline and results:
                improvement = results[0].win_rate - baseline.win_rate
                lines.append("")
                lines.append("SUMMARY:")
                lines.append(f"  Baseline win rate: {baseline.win_rate:.1f}%")
                lines.append(f"  Best win rate: {results[0].win_rate:.1f}%")
                lines.append(f"  Improvement: {improvement:+.1f}%")

        return "\n".join(lines)


if __name__ == "__main__":
    # Demo with mock results
    from scripts.optimization.search_space import SearchSpace

    space = SearchSpace()
    mock_results = [
        OptimizationResult(
            weights={'DVOA': 1.5, 'Matchup': 2.0, 'Volume': 1.8, 'Injury': 4.0,
                     'Trend': 1.2, 'GameScript': 2.5, 'Variance': 1.0, 'Weather': 1.5, 'HitRate': 2.8},
            wins=245, losses=175, voids=10, total_bets=420, win_rate=58.3, weeks_evaluated=[11, 12, 13]
        ),
        OptimizationResult(
            weights=space.get_default_weights(),
            wins=220, losses=200, voids=10, total_bets=420, win_rate=52.4, weeks_evaluated=[11, 12, 13]
        )
    ]

    reporter = ResultsReporter()
    reporter.print_results(mock_results, baseline=mock_results[1], top_n=5)
    print(reporter.format_weights_table(mock_results))
