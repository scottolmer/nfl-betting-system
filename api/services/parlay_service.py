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
