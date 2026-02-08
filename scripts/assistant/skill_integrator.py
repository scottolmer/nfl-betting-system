"""
Skill Integrator for Betting Assistant
Seamlessly invokes existing skills from within conversation
"""

import subprocess
import json
from typing import Dict, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

project_root = Path(__file__).parent.parent.parent


class SkillIntegrator:
    """Invokes existing skills from within conversational interface"""

    def __init__(self):
        self.skill_map = {
            # Historical queries
            "historical_query": "chat-query",
            "performance_review": "performance-reporter",

            # Data operations
            "data_validation": "data-validator",
            "odds_fetch": "odds-fetcher",

            # Analysis
            "full_analysis": "nfl-betting-analyzer",
            "correlation_check": "custom-parlay",
            "parlay_rebuild": "parlay-rebuilder",

            # Calibration & Performance
            "agent_calibration": "agent-calibrator",
            "backtest": "backtester",

            # Results
            "grade_results": "results-grader",

            # Monitoring
            "line_monitor": "line-monitor",
            "injury_check": "injury-tracker",
        }

    def invoke_skill(self, skill_type: str, args: str = "",
                    capture_output: bool = True) -> Tuple[bool, str]:
        """
        Invoke a skill and return results

        Args:
            skill_type: Type of skill to invoke (from skill_map)
            args: Arguments to pass to skill
            capture_output: Whether to capture and return output

        Returns:
            (success, output) tuple
        """
        skill_name = self.skill_map.get(skill_type)

        if not skill_name:
            logger.error(f"Unknown skill type: {skill_type}")
            return False, f"Unknown skill: {skill_type}"

        logger.info(f"Invoking skill: {skill_name} with args: {args}")

        try:
            # For now, we'll return a placeholder since skills require
            # the full Claude Code environment to execute
            # In production, this would invoke via the skill system

            return self._mock_skill_invocation(skill_name, args)

        except Exception as e:
            logger.error(f"Failed to invoke skill {skill_name}: {e}")
            return False, str(e)

    def _mock_skill_invocation(self, skill_name: str, args: str) -> Tuple[bool, str]:
        """
        Mock skill invocation for testing
        In production, this would call the actual skill
        """
        mock_responses = {
            "chat-query": self._mock_chat_query(args),
            "performance-reporter": self._mock_performance_reporter(args),
            "data-validator": self._mock_data_validator(args),
            "agent-calibrator": self._mock_agent_calibrator(args),
        }

        response = mock_responses.get(skill_name, (True, f"[Skill {skill_name} would be invoked with args: {args}]"))
        return response

    def _mock_chat_query(self, query: str) -> Tuple[bool, str]:
        """Mock chat-query skill response"""
        return (True,
                f"Historical Query Results:\n"
                f"Query: {query}\n\n"
                f"[This would invoke the chat-query skill to search the database]\n"
                f"[Results would show historical performance, hit rates, ROI, etc.]")

    def _mock_performance_reporter(self, args: str) -> Tuple[bool, str]:
        """Mock performance-reporter skill response"""
        return (True,
                "Performance Dashboard:\n"
                "======================\n"
                "Season ROI: +12.5%\n"
                "Total Parlays: 45\n"
                "Won: 18 (40%)\n"
                "Lost: 25 (56%)\n"
                "Push: 2 (4%)\n\n"
                "Top Performing Agents:\n"
                "1. DVOA Agent - 68% accuracy\n"
                "2. Hit Rate Agent - 65% accuracy\n"
                "3. Injury Agent - 62% accuracy\n\n"
                "[Full dashboard would show charts, trends, Pareto analysis]")

    def _mock_data_validator(self, args: str) -> Tuple[bool, str]:
        """Mock data-validator skill response"""
        return (True,
                "Data Validation Results:\n"
                "========================\n"
                "DVOA Files: VALID\n"
                "Betting Lines: VALID (3516 props)\n"
                "Roster: VALID (463 players)\n"
                "Injuries: MISSING\n\n"
                "Quality Score: 8/10\n"
                "[Ready for analysis]")

    def _mock_agent_calibrator(self, args: str) -> Tuple[bool, str]:
        """Mock agent-calibrator skill response"""
        return (True,
                "Agent Calibration Report:\n"
                "=========================\n"
                "Week analyzed: Current\n"
                "Agents calibrated: 9\n\n"
                "Weight Adjustments:\n"
                "- DVOA Agent: 2.0 -> 2.1 (+0.1)\n"
                "- Hit Rate Agent: 2.0 -> 2.2 (+0.2)\n"
                "- Injury Agent: 3.0 -> 2.9 (-0.1)\n\n"
                "[Weights updated in database]")

    def invoke_chat_query(self, question: str) -> str:
        """
        Invoke chat-query skill for historical queries

        Args:
            question: Natural language question about historical data

        Returns:
            Query results as formatted string
        """
        success, output = self.invoke_skill("historical_query", question)
        if success:
            return output
        else:
            return f"Failed to execute historical query: {output}"

    def invoke_performance_reporter(self, week: Optional[int] = None) -> str:
        """
        Invoke performance-reporter skill

        Args:
            week: Specific week to analyze (None for full season)

        Returns:
            Performance report as formatted string
        """
        args = f"--week {week}" if week else ""
        success, output = self.invoke_skill("performance_review", args)
        if success:
            return output
        else:
            return f"Failed to generate performance report: {output}"

    def invoke_data_validator(self, week: int) -> str:
        """
        Invoke data-validator skill

        Args:
            week: Week number to validate

        Returns:
            Validation report as formatted string
        """
        success, output = self.invoke_skill("data_validation", f"--week {week}")
        if success:
            return output
        else:
            return f"Failed to validate data: {output}"

    def invoke_agent_calibrator(self, week: int) -> str:
        """
        Invoke agent-calibrator skill

        Args:
            week: Week number to calibrate against

        Returns:
            Calibration report as formatted string
        """
        success, output = self.invoke_skill("agent_calibration", f"--week {week}")
        if success:
            return output
        else:
            return f"Failed to calibrate agents: {output}"

    def format_skill_output(self, output: str, max_lines: int = 50) -> str:
        """Format skill output for conversational display"""
        lines = output.split('\n')
        if len(lines) > max_lines:
            lines = lines[:max_lines] + [f"... ({len(lines) - max_lines} more lines)"]
        return '\n'.join(lines)


if __name__ == "__main__":
    # Test skill integrator
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    integrator = SkillIntegrator()

    print("\n" + "="*70)
    print("TEST: Skill Integrator")
    print("="*70)

    # Test 1: Historical query
    print("\nTest 1: Historical Query")
    print("-"*70)
    result = integrator.invoke_chat_query("How did Week 14 perform?")
    print(result)

    # Test 2: Performance reporter
    print("\n\nTest 2: Performance Reporter")
    print("-"*70)
    result = integrator.invoke_performance_reporter()
    print(result)

    # Test 3: Data validator
    print("\n\nTest 3: Data Validator")
    print("-"*70)
    result = integrator.invoke_data_validator(week=15)
    print(result)

    # Test 4: Agent calibrator
    print("\n\nTest 4: Agent Calibrator")
    print("-"*70)
    result = integrator.invoke_agent_calibrator(week=14)
    print(result)

    print("\n" + "="*70)
