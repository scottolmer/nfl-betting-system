"""
Weight Optimization System

This package provides tools for optimizing agent weights through random search
across historical backtest data.

Modules:
- search_space: Define weight ranges and generate random configurations
- in_memory_grader: Fast grading without file I/O
- weight_optimizer: Main optimization engine
- results_reporter: Format and save optimization results
- run_optimization: CLI entry point
"""

# Lazy imports to avoid circular import issues
# Import directly from modules when needed rather than through this __init__
from .search_space import SearchSpace
from .in_memory_grader import InMemoryGrader
from .results_reporter import ResultsReporter

# WeightOptimizer is not imported here to avoid triggering the backtest imports
# Import it directly from weight_optimizer module when needed

__all__ = ['SearchSpace', 'InMemoryGrader', 'ResultsReporter']
