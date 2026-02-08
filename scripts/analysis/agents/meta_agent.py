"""
Meta-Agent - Claude-powered oversight for aggregated analysis
Reviews agent outputs to catch edge cases, evaluate agreement, and add narrative context.
"""

import logging
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ..models import PropAnalysis

logger = logging.getLogger(__name__)


@dataclass
class MetaAgentConfig:
    """Configuration for Meta-Agent"""
    enabled: bool = True
    min_confidence_threshold: int = 65  # Only review high-value picks
    model: str = "gemini-2.0-flash"
    max_tokens: int = 800
    max_adjustment: int = 10  # -10 to +10


@dataclass
class MetaAgentResult:
    """Result from Meta-Agent review"""
    confidence_adjustment: int = 0           # -10 to +10
    adjusted_confidence: int = 50            # Final after adjustment
    agent_agreement_score: float = 1.0       # 0-1
    disagreement_flags: List[str] = field(default_factory=list)
    narrative_factors: List[str] = field(default_factory=list)  # Coaching changes, revenge games, etc.
    edge_case_warnings: List[str] = field(default_factory=list)
    meta_rationale: str = ""                 # 2-3 sentence explanation
    recommendation_override: Optional[str] = None  # None, "UPGRADE", "DOWNGRADE", "FLAG"
    tokens_used: int = 0
    model_used: str = ""


class MetaAgent:
    """
    Claude-powered meta-agent that reviews aggregated analysis from the 9 Python agents.
    Provides intelligent oversight to catch edge cases, evaluate agent agreement,
    and add narrative context.
    """

    def __init__(self, config: MetaAgentConfig = None):
        self.config = config or MetaAgentConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._model = None  # Lazy init

    @property
    def client(self):
        """Lazy-initialize Gemini client"""
        if self._model is None:
            try:
                from ...core.gemini_client import GeminiClient
                self._model = GeminiClient(model_name=self.config.model)
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini client: {e}")
                self._model = None
        return self._model

    def should_review(self, analysis: 'PropAnalysis') -> bool:
        """Determine if this analysis warrants meta-agent review"""
        if not self.config.enabled:
            return False

        # Only review high-value picks
        return analysis.final_confidence >= self.config.min_confidence_threshold

    def review(self, analysis: 'PropAnalysis', context: Dict) -> MetaAgentResult:
        """
        Review an analysis and provide meta-level insights.

        Args:
            analysis: PropAnalysis object with agent_breakdown
            context: Full context dict with props, stats, etc.

        Returns:
            MetaAgentResult with adjustments and insights
        """
        original_confidence = analysis.final_confidence

        # Calculate agent agreement first (doesn't require API)
        agreement_score, disagreement_flags = self._calculate_agent_agreement(
            analysis.agent_breakdown
        )

        # If no client available, return neutral result with agreement info
        if self.client is None or not self.client.is_available:
            self.logger.warning("Gemini client unavailable - returning neutral result")
            return MetaAgentResult(
                confidence_adjustment=0,
                adjusted_confidence=original_confidence,
                agent_agreement_score=agreement_score,
                disagreement_flags=disagreement_flags,
                meta_rationale="Meta-agent API unavailable",
                model_used="none"
            )

        try:
            # Build prompts
            system_prompt = self._build_system_prompt()
            review_prompt = self._build_review_prompt(analysis, context, agreement_score, disagreement_flags)

            # Call Gemini API
            # GeminiClient handles JSON parsing internally
            result_json = self.client.generate_json(
                prompt=review_prompt,
                system_instruction=system_prompt
            )

            if not result_json:
                raise ValueError("Empty response from Gemini")

            # Result is already a dict
            result = self._parse_json_result(result_json, original_confidence)
            
            result.agent_agreement_score = agreement_score
            result.disagreement_flags = disagreement_flags
            # OpenAI/Anthropic usage stats are different/not always available in simple Gemini response
            # We'll just track that we used it.
            result.model_used = self.config.model

            self.logger.info(
                f"Meta-agent review: {original_confidence} -> {result.adjusted_confidence} "
                f"({result.confidence_adjustment:+d}), agreement: {agreement_score:.2f}"
            )

            return result

        except Exception as e:
            self.logger.error(f"Meta-agent API call failed: {e}")
            # Return neutral result on failure
            return MetaAgentResult(
                confidence_adjustment=0,
                adjusted_confidence=original_confidence,
                agent_agreement_score=agreement_score,
                disagreement_flags=disagreement_flags,
                meta_rationale=f"Meta-agent review failed: {str(e)[:50]}",
                model_used="error"
            )

    def _calculate_agent_agreement(self, agent_breakdown: Dict) -> Tuple[float, List[str]]:
        """
        Calculate agent agreement score and identify disagreements.

        Returns:
            Tuple of (agreement_score 0-1, list of disagreement flags)
        """
        if not agent_breakdown:
            return 1.0, []

        scores = [r.get('raw_score', 50) for r in agent_breakdown.values()]

        if len(scores) < 2:
            return 1.0, []

        # Calculate standard deviation as disagreement measure
        # Normalize to 0-1 where 1 = perfect agreement
        std_dev = np.std(scores)
        agreement = 1.0 - min(1.0, std_dev / 50)  # Normalized to 0-1

        # Flag specific disagreements
        flags = []
        over_agents = [name for name, r in agent_breakdown.items()
                       if r.get('raw_score', 50) >= 55]
        under_agents = [name for name, r in agent_breakdown.items()
                        if r.get('raw_score', 50) <= 45]

        if over_agents and under_agents:
            flags.append(f"Split decision: {', '.join(over_agents)} favor OVER; {', '.join(under_agents)} favor UNDER")

        # Flag extreme outliers
        mean_score = np.mean(scores)
        for name, r in agent_breakdown.items():
            score = r.get('raw_score', 50)
            if abs(score - mean_score) > 20:
                direction = "bullish" if score > mean_score else "bearish"
                flags.append(f"{name} is outlier ({direction}: {score} vs avg {mean_score:.0f})")

        return round(agreement, 3), flags

    def _build_system_prompt(self) -> str:
        """Build the system prompt for meta-agent"""
        return """You are a Meta-Agent reviewing NFL betting prop analysis from 9 specialized agents.

Your role is to:
1. Evaluate agent agreement/disagreement patterns
2. Identify narrative factors that rule-based agents might miss (revenge games, playoff implications, coaching changes, weather impacts, primetime performance, etc.)
3. Flag edge cases that warrant caution
4. Recommend conservative confidence adjustments ONLY when justified

Guidelines:
- Adjustments should be between -10 and +10 points
- Default to 0 adjustment unless there's clear reason to change
- Be conservative - only adjust when you identify specific factors the agents may have missed
- Focus on ADDING context, not second-guessing agent calculations

Output Format (JSON):
{
    "adjustment": 0,  // -10 to +10
    "override": null,  // null, "UPGRADE", "DOWNGRADE", or "FLAG"
    "narrative_factors": [],  // List of relevant narrative factors
    "edge_case_warnings": [],  // List of cautions/warnings
    "rationale": "2-3 sentence explanation"
}"""

    def _build_review_prompt(self, analysis: 'PropAnalysis', context: Dict,
                             agreement_score: float, disagreement_flags: List[str]) -> str:
        """Build the review prompt with analysis details"""
        prop = analysis.prop

        # Format agent breakdown
        agent_summary = []
        for name, data in sorted(analysis.agent_breakdown.items(),
                                 key=lambda x: x[1].get('raw_score', 50), reverse=True):
            score = data.get('raw_score', 50)
            direction = "OVER" if score >= 55 else "UNDER" if score <= 45 else "NEUTRAL"
            agent_summary.append(f"  - {name}: {score} ({direction})")

        agent_breakdown_str = "\n".join(agent_summary) if agent_summary else "  No agent data"

        # Format disagreement flags
        disagreements_str = "\n".join(f"  - {f}" for f in disagreement_flags) if disagreement_flags else "  None"

        # Extract relevant context info
        matchup_info = self._extract_matchup_context(prop, context)

        prompt = f"""Review this NFL prop analysis:

## Prop Details
- Player: {prop.player_name} ({prop.team} vs {prop.opponent})
- Position: {prop.position}
- Stat: {prop.stat_type}
- Line: {prop.line}
- Bet Type: {prop.bet_type}
- Week: {prop.week}

## Current Analysis
- Final Confidence: {analysis.final_confidence}
- Recommendation: {analysis.recommendation}
- Edge Explanation: {analysis.edge_explanation}

## Agent Breakdown (score/100, >50 = OVER likely)
{agent_breakdown_str}

## Agent Agreement
- Agreement Score: {agreement_score:.2f} (1.0 = perfect agreement)
- Disagreement Flags:
{disagreements_str}

## Matchup Context
{matchup_info}

Based on this analysis, provide your meta-review in JSON format.
Consider: Are there narrative factors the agents might have missed? Any edge cases to flag? Should confidence be adjusted?"""

        return prompt

    def _extract_matchup_context(self, prop, context: Dict) -> str:
        """Extract relevant matchup context for the review"""
        lines = []

        # Game info
        if prop.game_total:
            lines.append(f"- Game Total: {prop.game_total}")
        if prop.spread:
            lines.append(f"- Spread: {prop.spread:+.1f} ({'home' if prop.is_home else 'away'})")

        # Injury context
        injury_report = context.get('injury_report', {})
        if prop.player_name in injury_report:
            lines.append(f"- Player Injury Status: {injury_report[prop.player_name]}")

        # Team injuries
        team_injuries = injury_report.get(prop.team, [])
        if team_injuries:
            lines.append(f"- Team Injuries: {len(team_injuries)} players affected")

        return "\n".join(lines) if lines else "- No additional context available"

    def _parse_json_result(self, data: Dict, original_confidence: int) -> MetaAgentResult:
        """Parse JSON dictionary into MetaAgentResult"""
        try:
            # Clamp adjustment to max range
            adjustment = max(-self.config.max_adjustment,
                           min(self.config.max_adjustment,
                               int(data.get('adjustment', 0))))

            adjusted_confidence = max(0, min(100, original_confidence + adjustment))

            return MetaAgentResult(
                confidence_adjustment=adjustment,
                adjusted_confidence=adjusted_confidence,
                narrative_factors=data.get('narrative_factors', []),
                edge_case_warnings=data.get('edge_case_warnings', []),
                meta_rationale=data.get('rationale', ''),
                recommendation_override=data.get('override'),
            )

        except (KeyError, TypeError) as e:
            self.logger.warning(f"Failed to parse meta-agent response data: {e}")
            return MetaAgentResult(
                confidence_adjustment=0,
                adjusted_confidence=original_confidence,
                meta_rationale=f"Parse error - original analysis unchanged."
            )

    def __repr__(self) -> str:
        return f"MetaAgent(enabled={self.config.enabled}, model={self.config.model})"
