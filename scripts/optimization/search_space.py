"""
Search Space Definition for Weight Optimization

Defines the range of weights to explore for each agent and provides
methods to generate random weight configurations.
"""

import random
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class AgentWeightRange:
    """Defines the min/max weight range for a single agent."""
    name: str
    min_weight: float
    max_weight: float
    default: float


class SearchSpace:
    """
    Defines the search space for agent weight optimization.

    Each agent has a configurable min/max weight range.
    Generates random configurations by sampling uniformly from each range.
    """

    # Default weight ranges for each agent
    # Updated based on offseason calibration analysis (weeks 11-16 graded data)
    # REMOVED: Trend (68% neutral), Weather (no data), HitRate (no predictive value)
    # - Matchup: 38.1% accuracy on strong signals (worse than random) -> reduced
    # - Volume: 44.4% accuracy on strong signals -> reduced
    # - Injury: High weight confirmed as valuable (4.72 in best config)
    # - DVOA: 50.5% accuracy, still useful (3.23 in best config)
    DEFAULT_RANGES = {
        'DVOA': AgentWeightRange('DVOA', 0.5, 4.0, 3.2),
        'Matchup': AgentWeightRange('Matchup', 0.1, 1.5, 0.5),
        'Volume': AgentWeightRange('Volume', 0.1, 1.5, 0.75),
        'Injury': AgentWeightRange('Injury', 2.0, 5.0, 4.7),
        'GameScript': AgentWeightRange('GameScript', 0.1, 2.0, 0.82),
        'Variance': AgentWeightRange('Variance', 0.5, 3.5, 2.4),
    }

    def __init__(self,
                 min_weight: float = None,
                 max_weight: float = None,
                 custom_ranges: Dict[str, Tuple[float, float]] = None):
        """
        Initialize the search space.

        Args:
            min_weight: Global minimum weight (overrides individual agent mins)
            max_weight: Global maximum weight (overrides individual agent maxs)
            custom_ranges: Dict of agent_name -> (min, max) tuples for custom ranges
        """
        self.ranges = {}

        for name, default_range in self.DEFAULT_RANGES.items():
            min_w = default_range.min_weight
            max_w = default_range.max_weight

            # Apply global overrides
            if min_weight is not None:
                min_w = max(min_weight, min_w)
            if max_weight is not None:
                max_w = min(max_weight, max_w)

            # Apply custom ranges
            if custom_ranges and name in custom_ranges:
                min_w, max_w = custom_ranges[name]

            self.ranges[name] = AgentWeightRange(
                name=name,
                min_weight=min_w,
                max_weight=max_w,
                default=default_range.default
            )

    def get_agent_names(self) -> List[str]:
        """Return list of all agent names."""
        return list(self.ranges.keys())

    def get_default_weights(self) -> Dict[str, float]:
        """Return the default (baseline) weights."""
        return {name: r.default for name, r in self.ranges.items()}

    def generate_random_config(self) -> Dict[str, float]:
        """
        Generate a single random weight configuration.

        Returns:
            Dict mapping agent names to randomly sampled weights
        """
        config = {}
        for name, range_info in self.ranges.items():
            weight = random.uniform(range_info.min_weight, range_info.max_weight)
            # Round to 2 decimal places for cleaner output
            config[name] = round(weight, 2)
        return config

    def generate_random_configurations(self, n: int, include_default: bool = True) -> List[Dict[str, float]]:
        """
        Generate n random weight configurations.

        Args:
            n: Number of configurations to generate
            include_default: If True, includes baseline weights as first config

        Returns:
            List of weight configuration dicts
        """
        configs = []

        # Optionally include default weights first
        if include_default:
            configs.append(self.get_default_weights())
            n -= 1

        for _ in range(n):
            configs.append(self.generate_random_config())

        return configs

    def describe(self) -> str:
        """Return a human-readable description of the search space."""
        lines = ["Agent Weight Search Space:"]
        lines.append("-" * 50)
        for name, r in self.ranges.items():
            lines.append(f"  {name:12s}: [{r.min_weight:.2f}, {r.max_weight:.2f}] (default: {r.default:.2f})")
        return "\n".join(lines)


if __name__ == "__main__":
    # Demo usage
    space = SearchSpace()
    print(space.describe())
    print("\nGenerating 3 random configurations:")
    configs = space.generate_random_configurations(3)
    for i, config in enumerate(configs):
        print(f"\nConfig {i+1}:")
        for name, weight in config.items():
            print(f"  {name}: {weight:.2f}")
