"""Parlay generation API endpoints"""

from fastapi import APIRouter, Depends, Query, HTTPException
from api.dependencies import get_api_key
from api.services.analysis_service import AnalysisService
from api.services.parlay_service import ParlayService
from api.schemas.parlays import ParlayResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
analysis_service = AnalysisService(data_dir="data")
parlay_service = ParlayService()


@router.get(
    "/prebuilt",
    response_model=List[ParlayResponse],
    summary="Get pre-built parlays",
    description="""
    Generate 6 pre-built parlays from analyzed props.

    Uses existing ParlayBuilder to create diversified parlays with:
    - Player diversity constraints (max 3 parlays per player)
    - Mixed leg sizes (2-leg, 3-leg, 4-leg, 5-leg)
    - Risk level assessment (LOW, MEDIUM, HIGH)
    - Combined confidence scores

    100% code reuse of existing parlay generation logic.
    """
)
async def get_prebuilt_parlays(
    week: int = Query(..., ge=1, le=18, description="NFL week number"),
    min_confidence: int = Query(58, ge=0, le=100, description="Minimum confidence for props in parlays"),
    team: Optional[str] = Query(None, description="Optional: filter to specific team(s)"),
    api_key: str = Depends(get_api_key)
):
    """
    Generate 6 pre-built parlays for a given week.

    Uses existing ParlayBuilder (100% reuse).
    """
    try:
        # First, analyze all props for the week (get raw PropAnalysis objects for parlay builder)
        logger.info(f"Analyzing props for week {week} to generate parlays...")
        all_analyses = await analysis_service.get_raw_analyses_for_week(
            week=week,
            min_confidence=min_confidence,
            team=team
        )

        if len(all_analyses) < 2:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient props found for week {week} with min_confidence {min_confidence}. Need at least 2 props."
            )

        # Generate parlays using existing builder
        parlays = await parlay_service.generate_prebuilt_parlays(
            all_analyses=all_analyses,
            min_confidence=min_confidence
        )

        if not parlays:
            raise HTTPException(
                status_code=404,
                detail="No valid parlays could be generated with the given criteria"
            )

        return parlays

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating parlays: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating parlays: {str(e)}"
        )
