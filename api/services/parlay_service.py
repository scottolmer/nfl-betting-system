from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.analysis.models import Parlay, PropAnalysis, PlayerProp
from scripts.analysis.dependency_analyzer import DependencyAnalyzer
from api.schemas.parlays import ParlayResponse, ParlayLegResponse
from api.schemas.parlay_grading import ParlayGradeRequest, ParlayGradeResponse, ParlayLegRequest, SwapSuggestion
from typing import List
import logging
import math
from starlette.concurrency import run_in_threadpool

logger = logging.getLogger(__name__)


class ParlayService:
    """
    Service layer wrapping existing ParlayBuilder.

    This class provides a thin wrapper around the existing ParlayBuilder,
    achieving 100% code reuse of the parlay generation logic.
    """

    def __init__(self):
        """Initialize service with existing parlay builder"""
        self.builder = ParlayBuilder()
        self.grader = DependencyAnalyzer()
        logger.info("✓ ParlayService initialized (reusing ParlayBuilder)")

    async def grade_parlay(self, legs: List[ParlayLegRequest]) -> ParlayGradeResponse:
        """
        Grade a user-submitted parlay.
        """
        # 1. Convert requests to PropAnalysis objects
        prop_analyses = []
        for leg in legs:
            # Create dummy PlayerProp
            prop = PlayerProp(
                player_name=leg.player_name,
                team=leg.team,
                opponent=leg.opponent,
                stat_type=leg.stat_type,
                line=leg.line,
                position=leg.position or "UNKNOWN",
                bet_type=leg.bet_type,
                week=18
            )
            # Create dummy PropAnalysis
            analysis = PropAnalysis(
                prop=prop,
                final_confidence=leg.confidence,
                recommendation="REVIEW", # Required field
                rationale=[], # Required field
                agent_breakdown={}, # Required field
                edge_explanation="" # Required field
            )
            # Override fields that might be missing in constructor if PropAnalysis has defaults?
            # From view_file, PropAnalysis has: prop, final_confidence, recommendation, rationale, agent_breakdown, edge_explanation
            # No defaults for them except created_at, top_contributing_agents, meta_agent_result.
            
            prop_analyses.append(analysis)

        # 2. Construct Parlay object
        # Calculate naive combined confidence (product)
        if not prop_analyses:
            return ParlayGradeResponse(
                grade="F", adjusted_confidence=0, original_confidence=0,
                recommendation="AVOID", analysis="Empty parlay", 
                risk_factors=["No legs provided"], 
                implied_probability=0, true_probability=0, value_edge=0
            )

        # Calculate Raw Joint Probability (Product of probabilities)
        raw_prob = 1.0
        for leg in legs:
            raw_prob *= (leg.confidence / 100.0)
        
        parlay = Parlay(
            legs=prop_analyses,
            parlay_type=f"{len(legs)}-leg",
            risk_level="UNKNOWN",
            rationale="User submitted",
        )

        # 3. Analyze Dependencies
        # Run blocking Gemini call in threadpool
        analysis = await run_in_threadpool(self.grader.analyze_parlay_dependencies, parlay)
        
        adj_conf = analysis.get("adjusted_confidence", 0)
        recommendation = analysis.get("recommendation", "REVIEW")
        risk_flags = analysis.get("risk_flags", [])
        if analysis.get("correlation_adjustment", {}).get("adjustment_value", 0) < 0:
             risk_flags.append(f"Correlation Penalty: {analysis['correlation_adjustment']['adjustment_value']}%")

        # 4. Grading Logic
        if adj_conf >= 70:
            grade = "A+"
        elif adj_conf >= 60:
            grade = "A"
        elif adj_conf >= 50:
            grade = "B"
        elif adj_conf >= 40:
            grade = "C"
        elif adj_conf >= 30:
            grade = "D"
        else:
            grade = "F"

        # 5. Value Analysis
        # Estimate Implied Probability based on leg count (assuming standard parlay payouts)
        implied_prob = (0.5238) ** len(legs) * 100 
        
        # Our True Probability is the Adjusted Confidence
        true_prob = adj_conf 
        
        value_edge = true_prob - implied_prob

        analysis_text = (
            f"This {len(legs)}-leg parlay has an adjusted win probability of {adj_conf:.1f}% "
            f"(Grade: {grade}). We detected {len(risk_flags)} risk factors."
        )
        if value_edge > 5:
            analysis_text += " Great value estimated against standard book odds."
        elif value_edge < -5:
            analysis_text += " Poor value estimated; book odds payout is likely too low for the risk."

        return ParlayGradeResponse(
            grade=grade,
            adjusted_confidence=adj_conf,
            original_confidence=raw_prob * 100,
            recommendation=recommendation,
            analysis=analysis_text,
            risk_factors=risk_flags,
            implied_probability=round(implied_prob, 1),
            true_probability=round(true_prob, 1),
            value_edge=round(value_edge, 1),
            suggestions=[] # TODO: Implement Smart Swaps
        )

    async def generate_prebuilt_parlays(
        self,
        all_analyses: List[PropAnalysis],
        min_confidence: int = 58
    ) -> List[ParlayResponse]:
        """
        Generate 6 pre-built parlays using EXISTING builder.

        NO CHANGES to ParlayBuilder - pure wrapper.
        """
        logger.info(f"Generating parlays from {len(all_analyses)} props with min_confidence={min_confidence}")

        # Use EXISTING build_parlays method (100% reuse)
        parlays_dict = self.builder.build_parlays(all_analyses, min_confidence=min_confidence)

        # Return a diverse mix: best of each leg count, then fill remaining slots
        diverse_picks = []
        for leg_type in ['2-leg', '3-leg', '4-leg', '5-leg', '6-leg']:
            type_parlays = parlays_dict.get(leg_type, [])
            if type_parlays:
                # Sort this type by confidence and take the best one
                type_parlays.sort(key=lambda p: p.combined_confidence, reverse=True)
                diverse_picks.append(type_parlays[0])

        # Fill remaining slots (up to 10) with the best unused parlays
        picked_ids = set(id(p) for p in diverse_picks)
        remaining = []
        for parlays in parlays_dict.values():
            for p in parlays:
                if id(p) not in picked_ids:
                    remaining.append(p)
        remaining.sort(key=lambda p: p.combined_confidence, reverse=True)
        diverse_picks.extend(remaining[:10 - len(diverse_picks)])

        # Sort final list: group by leg count ascending, then confidence descending
        diverse_picks.sort(key=lambda p: (len(p.legs), -p.combined_confidence))

        total_all = sum(len(v) for v in parlays_dict.values())
        logger.info(f"✓ Generated {total_all} parlays, returning {len(diverse_picks)} (diverse mix)")

        # Convert to API response models with unique index
        return [self._to_response(p, i) for i, p in enumerate(diverse_picks)]

    def _to_response(self, parlay: Parlay, index: int = 0) -> ParlayResponse:
        """Convert Parlay dataclass to Pydantic response schema"""
        import hashlib

        # Generate unique ID based on parlay content + leg player names
        leg_names = "_".join(leg.prop.player_name for leg in parlay.legs)
        parlay_content = f"{parlay.parlay_type}_{parlay.combined_confidence}_{leg_names}_{index}"
        parlay_id = hashlib.md5(parlay_content.encode()).hexdigest()[:12]

        # Generate name
        parlay_name = f"{parlay.parlay_type.upper()} ({parlay.risk_level})"

        return ParlayResponse(
            id=parlay_id,
            name=parlay_name,
            parlay_type=parlay.parlay_type,
            combined_confidence=parlay.combined_confidence,
            risk_level=parlay.risk_level,
            rationale=parlay.rationale,
            leg_count=len(parlay.legs),
            legs=[
                ParlayLegResponse(
                    player_name=leg.prop.player_name,
                    team=leg.prop.team,
                    opponent=leg.prop.opponent,
                    stat_type=leg.prop.stat_type,
                    bet_type=leg.prop.bet_type,
                    line=leg.prop.line,
                    confidence=leg.final_confidence
                )
                for leg in parlay.legs
            ]
        )
