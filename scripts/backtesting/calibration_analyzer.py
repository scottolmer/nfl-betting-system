"""
Calibration Analyzer - Bridge between Backtest Results and Weight Manager

Analyzes graded backtest results to calculate per-agent performance metrics,
then feeds those to AgentWeightManager for automated weight adjustments.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Direct import to avoid circular dependency issues
import importlib.util
spec = importlib.util.spec_from_file_location(
    "agent_weight_manager",
    project_root / "scripts" / "analysis" / "agent_weight_manager.py"
)
agent_weight_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_weight_module)
AgentWeightManager = agent_weight_module.AgentWeightManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fix Windows console encoding for emoji support
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


@dataclass
class AgentStats:
    """Track performance statistics for a single agent."""
    name: str
    total_predictions: int = 0
    wins: int = 0
    losses: int = 0

    # Track by confidence buckets
    high_conf_predictions: int = 0  # score >= 70
    high_conf_wins: int = 0

    medium_conf_predictions: int = 0  # 50 <= score < 70
    medium_conf_wins: int = 0

    # Track direction accuracy
    over_predictions: int = 0
    over_wins: int = 0
    under_predictions: int = 0
    under_wins: int = 0

    # Sum of confidence scores for overconfidence calculation
    total_confidence_sum: float = 0.0
    aligned_predictions: int = 0  # predictions where agent agreed with final bet

    # Track when agent disagreed with final bet direction
    contrarian_correct: int = 0  # agent disagreed but was right
    contrarian_wrong: int = 0    # agent disagreed and was wrong

    @property
    def accuracy(self) -> float:
        """Overall accuracy when agent aligned with bet direction."""
        if self.aligned_predictions == 0:
            return 0.0
        return self.wins / self.aligned_predictions

    @property
    def high_conf_accuracy(self) -> float:
        """Accuracy on high-confidence predictions."""
        if self.high_conf_predictions == 0:
            return 0.0
        return self.high_conf_wins / self.high_conf_predictions

    @property
    def average_confidence(self) -> float:
        """Average confidence score when aligned."""
        if self.aligned_predictions == 0:
            return 0.0
        return self.total_confidence_sum / self.aligned_predictions

    @property
    def overconfidence(self) -> float:
        """
        Overconfidence = average confidence - actual accuracy
        Positive = agent thinks it's better than it is
        Negative = agent is underconfident (conservative)
        """
        if self.aligned_predictions == 0:
            return 0.0
        # Convert confidence from 0-100 scale to 0-1
        avg_conf_normalized = self.average_confidence / 100.0
        return avg_conf_normalized - self.accuracy

    @property
    def contrarian_value(self) -> float:
        """
        How often the agent was right when it disagreed with the final bet.
        High value = agent provides useful contrary signals.
        """
        total_contrarian = self.contrarian_correct + self.contrarian_wrong
        if total_contrarian == 0:
            return 0.0
        return self.contrarian_correct / total_contrarian


class CalibrationAnalyzer:
    """
    Analyzes graded backtest results to calculate agent performance metrics
    and recommend weight adjustments.
    """

    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 70
    MEDIUM_CONFIDENCE_THRESHOLD = 50

    def __init__(self, data_dir: Optional[str] = None, db_path: str = "bets.db"):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = Path(data_dir) if data_dir else (self.project_root / "data")
        self.results_dir = self.data_dir / "backtest_results"
        self.weight_manager = AgentWeightManager(db_path)

        # Agent statistics
        self.agent_stats: Dict[str, AgentStats] = {}

    def load_graded_results(self, weeks: List[int]) -> List[Dict]:
        """Load graded results from specified weeks."""
        all_results = []

        for week in weeks:
            graded_file = self.results_dir / f"graded_week_{week}.json"
            if not graded_file.exists():
                logger.warning(f"No graded results for Week {week}")
                continue

            with open(graded_file, 'r') as f:
                results = json.load(f)
                # Tag with week number
                for r in results:
                    r['week'] = week
                all_results.extend(results)
                logger.info(f"Loaded {len(results)} graded predictions from Week {week}")

        return all_results

    def analyze_agent_performance(self, graded_results: List[Dict]) -> Dict[str, AgentStats]:
        """
        Analyze each agent's performance across all graded predictions.

        For each prediction:
        - Check what direction the agent recommended (from agent's 'direction' field)
        - Check if agent agreed with the final bet direction
        - Track wins/losses when aligned vs contrarian
        """
        self.agent_stats = {}

        for pred in graded_results:
            result = pred.get('result', 'UNKNOWN')

            # Skip void/unknown results
            if result not in ['WIN', 'LOSS']:
                continue

            bet_won = (result == 'WIN')
            bet_direction = pred.get('bet_type', '').upper()
            agents = pred.get('agents', {})

            for agent_name, agent_data in agents.items():
                # Initialize agent stats if needed
                if agent_name not in self.agent_stats:
                    self.agent_stats[agent_name] = AgentStats(name=agent_name)

                stats = self.agent_stats[agent_name]
                stats.total_predictions += 1

                # Get agent's recommendation
                agent_score = agent_data.get('raw_score', 50)
                agent_direction = agent_data.get('direction', '').upper()

                # Check if agent agreed with final bet direction
                agent_aligned = (agent_direction == bet_direction)

                if agent_aligned:
                    # Agent agreed with the bet
                    stats.aligned_predictions += 1
                    stats.total_confidence_sum += agent_score

                    if bet_won:
                        stats.wins += 1
                    else:
                        stats.losses += 1

                    # Track by confidence level
                    if agent_score >= self.HIGH_CONFIDENCE_THRESHOLD:
                        stats.high_conf_predictions += 1
                        if bet_won:
                            stats.high_conf_wins += 1
                    elif agent_score >= self.MEDIUM_CONFIDENCE_THRESHOLD:
                        stats.medium_conf_predictions += 1
                        if bet_won:
                            stats.medium_conf_wins += 1

                    # Track by direction
                    if agent_direction == 'OVER':
                        stats.over_predictions += 1
                        if bet_won:
                            stats.over_wins += 1
                    elif agent_direction == 'UNDER':
                        stats.under_predictions += 1
                        if bet_won:
                            stats.under_wins += 1
                else:
                    # Agent disagreed with the bet (contrarian)
                    # If bet lost, agent was right to disagree
                    if not bet_won:
                        stats.contrarian_correct += 1
                    else:
                        stats.contrarian_wrong += 1

        return self.agent_stats

    def generate_performance_report(self) -> str:
        """Generate a detailed performance report for all agents."""
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("AGENT CALIBRATION REPORT")
        lines.append("=" * 80)

        # Sort by accuracy (descending)
        sorted_agents = sorted(
            self.agent_stats.values(),
            key=lambda x: x.accuracy if x.aligned_predictions > 0 else 0,
            reverse=True
        )

        for stats in sorted_agents:
            if stats.aligned_predictions < 5:
                continue  # Skip agents with too few samples

            lines.append(f"\n{'─' * 40}")
            lines.append(f"AGENT: {stats.name}")
            lines.append(f"{'─' * 40}")

            # Overall metrics
            lines.append(f"  Aligned Predictions: {stats.aligned_predictions}")
            lines.append(f"  Overall Accuracy:    {stats.accuracy:.1%} ({stats.wins}W / {stats.losses}L)")
            lines.append(f"  Avg Confidence:      {stats.average_confidence:.1f}")
            lines.append(f"  Overconfidence:      {stats.overconfidence:+.1%}")

            # High confidence breakdown
            if stats.high_conf_predictions > 0:
                lines.append(f"\n  High Confidence (≥70):")
                lines.append(f"    Predictions: {stats.high_conf_predictions}")
                lines.append(f"    Accuracy:    {stats.high_conf_accuracy:.1%}")

            # Direction breakdown
            if stats.over_predictions > 0:
                over_acc = stats.over_wins / stats.over_predictions
                lines.append(f"\n  OVER predictions: {stats.over_predictions} ({over_acc:.1%} accurate)")
            if stats.under_predictions > 0:
                under_acc = stats.under_wins / stats.under_predictions
                lines.append(f"  UNDER predictions: {stats.under_predictions} ({under_acc:.1%} accurate)")

            # Contrarian analysis
            total_contrarian = stats.contrarian_correct + stats.contrarian_wrong
            if total_contrarian > 0:
                lines.append(f"\n  Contrarian Value: {stats.contrarian_value:.1%}")
                lines.append(f"    (Right when disagreed: {stats.contrarian_correct}/{total_contrarian})")

            # Assessment
            lines.append(f"\n  Assessment:")
            if stats.overconfidence > 0.10:
                lines.append(f"    ⚠️  SIGNIFICANTLY OVERCONFIDENT - reduce weight")
            elif stats.overconfidence > 0.05:
                lines.append(f"    📉 Moderately overconfident - consider reducing weight")
            elif stats.overconfidence < -0.10:
                lines.append(f"    📈 Underconfident - consider increasing weight")
            elif stats.accuracy > 0.55:
                lines.append(f"    ✅ Well-calibrated and accurate")
            elif stats.accuracy < 0.45:
                lines.append(f"    ⚠️  Low accuracy - review agent logic")
            else:
                lines.append(f"    ↔️  Neutral performance")

        lines.append("\n" + "=" * 80)

        return "\n".join(lines)

    def prepare_weight_adjustments(self) -> Dict[str, Dict]:
        """
        Prepare agent performance data for the AgentWeightManager.

        Returns dict in format expected by auto_adjust_weights():
        {
            'AgentName': {
                'accuracy': float,
                'overconfidence': float,
                'sample_size': int
            }
        }
        """
        performance_data = {}

        for agent_name, stats in self.agent_stats.items():
            if stats.aligned_predictions < 10:
                continue  # Skip agents with insufficient data

            performance_data[agent_name] = {
                'accuracy': stats.accuracy,
                'overconfidence': stats.overconfidence,
                'sample_size': stats.aligned_predictions,
                'high_conf_accuracy': stats.high_conf_accuracy,
                'contrarian_value': stats.contrarian_value
            }

        return performance_data

    def run_calibration(
        self,
        weeks: List[int],
        dry_run: bool = True,
        save_report: bool = True
    ) -> Tuple[str, List[Dict]]:
        """
        Run full calibration analysis and optionally apply weight adjustments.

        Args:
            weeks: List of week numbers to analyze
            dry_run: If True, show proposed changes without applying
            save_report: If True, save report to file

        Returns:
            Tuple of (report_text, adjustments_list)
        """
        logger.info(f"Starting calibration analysis for weeks: {weeks}")

        # Load graded results
        graded_results = self.load_graded_results(weeks)

        if not graded_results:
            logger.error("No graded results found. Run grade_results.py first.")
            return "No graded results found.", []

        logger.info(f"Analyzing {len(graded_results)} total predictions...")

        # Analyze performance
        self.analyze_agent_performance(graded_results)

        # Generate report
        report = self.generate_performance_report()
        print(report)

        # Prepare and apply adjustments
        performance_data = self.prepare_weight_adjustments()

        if not performance_data:
            logger.warning("Insufficient data for weight adjustments")
            return report, []

        # Show current weights
        print("\n" + "=" * 80)
        print("CURRENT WEIGHTS vs PROPOSED ADJUSTMENTS")
        print("=" * 80)
        self.weight_manager.print_current_weights()

        # Calculate adjustments
        # Use the max week as the "week" parameter for tracking
        max_week = max(weeks)
        adjustments = self.weight_manager.auto_adjust_weights(
            agent_performance=performance_data,
            week=max_week,
            dry_run=dry_run
        )

        # Print adjustment summary
        self.weight_manager.print_adjustment_summary(adjustments)

        if dry_run:
            print("\n⚠️  DRY RUN MODE - No changes applied")
            print("Run with --apply to apply these adjustments\n")
        else:
            print("\n✅ Weight adjustments applied to database\n")

        # Save report if requested
        if save_report:
            report_file = self.results_dir / f"calibration_report_weeks_{'_'.join(map(str, weeks))}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
                f.write("\n\n" + "=" * 80 + "\n")
                f.write("WEIGHT ADJUSTMENTS\n")
                f.write("=" * 80 + "\n")
                for adj in adjustments:
                    f.write(f"\n{adj['agent']}: {adj['old_weight']:.2f} -> {adj['new_weight']:.2f}")
                    f.write(f"\n  Reason: {adj['reason']}\n")
            logger.info(f"Report saved to {report_file}")

        return report, adjustments

    def analyze_by_stat_type(self, graded_results: List[Dict]) -> Dict[str, Dict]:
        """
        Analyze agent performance broken down by stat type (pass_yds, rush_yds, etc.)
        Useful for identifying if agents perform differently on different prop types.
        """
        stat_type_performance = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'total': 0}))

        for pred in graded_results:
            result = pred.get('result', 'UNKNOWN')
            if result not in ['WIN', 'LOSS']:
                continue

            bet_won = (result == 'WIN')
            stat_type = pred.get('stat_type', 'unknown').lower()
            bet_direction = pred.get('bet_type', '').upper()
            agents = pred.get('agents', {})

            for agent_name, agent_data in agents.items():
                agent_direction = agent_data.get('direction', '').upper()

                if agent_direction == bet_direction:
                    stat_type_performance[agent_name][stat_type]['total'] += 1
                    if bet_won:
                        stat_type_performance[agent_name][stat_type]['wins'] += 1

        return dict(stat_type_performance)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Analyze backtest results and calibrate agent weights')
    parser.add_argument('--weeks', type=str, required=True,
                        help='Weeks to analyze (e.g., "11-16" or "11,12,14")')
    parser.add_argument('--apply', action='store_true',
                        help='Apply weight adjustments (default: dry run)')
    parser.add_argument('--no-report', action='store_true',
                        help='Do not save report to file')

    args = parser.parse_args()

    # Parse weeks
    weeks = []
    if '-' in args.weeks:
        start, end = map(int, args.weeks.split('-'))
        weeks = list(range(start, end + 1))
    else:
        weeks = [int(w.strip()) for w in args.weeks.split(',')]

    # Run calibration
    analyzer = CalibrationAnalyzer()
    analyzer.run_calibration(
        weeks=weeks,
        dry_run=not args.apply,
        save_report=not args.no_report
    )


if __name__ == "__main__":
    main()
