"""Parlay Service - Wraps existing ParlayBuilder for API use (100% code reuse)"""

from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.analysis.models import Parlay, PropAnalysis
from api.schemas.parlays import ParlayResponse, ParlayLegResponse
from typing import List
import logging

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
        logger.info("✓ ParlayService initialized (reusing ParlayBuilder)")

    async def generate_prebuilt_parlays(
        self,
        all_analyses: List[PropAnalysis],
        min_confidence: int = 58
    ) -> List[ParlayResponse]:
        """
        Generate 6 pre-built parlays using EXISTING builder.

        NO CHANGES to ParlayBuilder - pure wrapper.

        Args:
            all_analyses: List of PropAnalysis objects from analyzer
            min_confidence: Minimum confidence for props to include in parlays

        Returns:
            List of top 6 ParlayResponse objects sorted by confidence
        """
        logger.info(f"Generating parlays from {len(all_analyses)} props with min_confidence={min_confidence}")

        # Use EXISTING build_parlays method (100% reuse)
        parlays_dict = self.builder.build_parlays(all_analyses, min_confidence=min_confidence)

        # Flatten to list and take top 6
        all_parlays = []
        for parlay_type, parlays in parlays_dict.items():
            all_parlays.extend(parlays)

        # Sort by confidence and take top 6
        all_parlays.sort(key=lambda p: p.combined_confidence, reverse=True)
        top_6 = all_parlays[:6]

        logger.info(f"✓ Generated {len(all_parlays)} parlays, returning top 6")

        # Convert to API response models
        return [self._to_response(p) for p in top_6]

    def _to_response(self, parlay: Parlay) -> ParlayResponse:
        """Convert Parlay dataclass to Pydantic response schema"""
        import hashlib

        # Generate unique ID based on parlay content
        parlay_content = f"{parlay.parlay_type}_{parlay.combined_confidence}_{len(parlay.legs)}"
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
