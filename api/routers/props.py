"""Props analysis API endpoints"""

from fastapi import APIRouter, Depends, Query, HTTPException
from api.dependencies import get_api_key
from api.services.analysis_service import AnalysisService
from api.schemas.props import PropAnalysisResponse
from api.schemas.line_adjustment import LineAdjustmentRequest, LineAdjustmentResponse
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
analysis_service = AnalysisService(data_dir="data")


@router.get(
    "/analyze",
    response_model=List[PropAnalysisResponse],
    summary="Analyze props for a given week",
    description="""
    Analyze player props using 9-agent system:
    - DVOA (team efficiency)
    - Matchup (position-specific defense)
    - Volume (snap/target share)
    - GameScript (game total/spread)
    - Injury (health status)
    - Trend (recent performance)
    - Variance (prop reliability)
    - HitRate (historical accuracy)
    - Weather (disabled)

    Returns props with confidence scores (0-100) and agent breakdowns.

    **Enhanced Filtering:**
    - Confidence range: `min_confidence=60&max_confidence=80`
    - Multiple teams: `teams=KC,BUF,DET`
    - Multiple positions: `positions=QB,WR`
    - Combine filters: `teams=KC,BUF&positions=QB,WR&min_confidence=65`
    """
)
async def analyze_props(
    week: int = Query(..., ge=1, le=18, description="NFL week number"),
    min_confidence: int = Query(60, ge=0, le=100, description="Minimum confidence threshold"),
    max_confidence: Optional[int] = Query(None, ge=0, le=100, description="Maximum confidence threshold (optional)"),
    team: Optional[str] = Query(None, description="Filter by single team (e.g., KC) - use 'teams' for multiple"),
    teams: Optional[str] = Query(None, description="Filter by multiple teams, comma-separated (e.g., KC,BUF,DET)"),
    position: Optional[str] = Query(None, description="Filter by single position (e.g., QB) - use 'positions' for multiple"),
    positions: Optional[str] = Query(None, description="Filter by multiple positions, comma-separated (e.g., QB,WR,RB)"),
    stat_type: Optional[str] = Query(None, description="Filter by stat type (Pass Yds, Rush Yds, Rec Yds, etc.)"),
    bet_type: Optional[str] = Query(None, description="Filter by bet direction (OVER, UNDER)"),
    limit: Optional[int] = Query(None, ge=1, le=200, description="Maximum number of results to return"),
    api_key: str = Depends(get_api_key)
):
    """
    Analyze props for a given week with enhanced filtering options.

    Uses existing PropAnalyzer (9 agents) - 100% code reuse.

    **New Enhanced Filters:**
    - `max_confidence`: Set maximum confidence (e.g., 60-80 range)
    - `teams`: Multiple teams comma-separated (e.g., "KC,BUF,DET")
    - `positions`: Multiple positions comma-separated (e.g., "QB,WR")
    """
    try:
        props = await analysis_service.analyze_props_for_week(
            week=week,
            min_confidence=min_confidence,
            max_confidence=max_confidence,
            team=team,
            teams=teams,
            position=position,
            positions=positions,
            stat_type=stat_type,
            bet_type=bet_type,
            limit=limit
        )
        return props
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Data not found for week {week}. {str(e)}"
        )
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Analysis error: {str(e)}"
        )


@router.get(
    "/top",
    response_model=List[PropAnalysisResponse],
    summary="Get top props by confidence",
    description="Get top N props sorted by confidence score."
)
async def get_top_props(
    week: int = Query(..., ge=1, le=18, description="NFL week number"),
    limit: int = Query(20, ge=1, le=100, description="Number of top props to return"),
    bet_type: Optional[str] = Query(None, description="Filter by OVER or UNDER"),
    api_key: str = Depends(get_api_key)
):
    """Get top N props by confidence"""
    try:
        props = await analysis_service.analyze_props_for_week(
            week=week,
            min_confidence=50,  # Lower threshold to get more props, then take top N
            bet_type=bet_type,
            limit=limit
        )
        return props
    except Exception as e:
        logger.error(f"Error getting top props: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting top props: {str(e)}"
        )


@router.get(
    "/team/{team_abbr}",
    response_model=List[PropAnalysisResponse],
    summary="Get props for a specific team",
    description="Get all analyzed props for players on a specific team."
)
async def get_team_props(
    team_abbr: str,
    week: int = Query(..., ge=1, le=18, description="NFL week number"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of results"),
    api_key: str = Depends(get_api_key)
):
    """Get props for a specific team"""
    try:
        props = await analysis_service.analyze_props_for_week(
            week=week,
            min_confidence=50,
            team=team_abbr.upper(),
            limit=limit
        )
        return props
    except Exception as e:
        logger.error(f"Error getting team props: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error getting team props: {str(e)}"
        )


@router.post(
    "/adjust-line",
    response_model=LineAdjustmentResponse,
    summary="Adjust line and recalculate confidence",
    description="""
    Adjust prop line for Pick 6 or other platforms and recalculate confidence.

    **Critical for Pick 6 compatibility** - lines often differ between regular props and Pick 6.

    Example: Travis Kelce receiving yards might be 56.5 in regular props but 58.5 in Pick 6.
    This endpoint recalculates confidence for the new line using the same 9-agent system.

    Returns both original and adjusted confidence scores so you can see the impact.
    """
)
async def adjust_line(
    request: LineAdjustmentRequest,
    api_key: str = Depends(get_api_key)
):
    """
    Adjust line for Pick 6 compatibility and recalculate confidence.

    FREE feature - critical for Pick 6 users.
    """
    try:
        result = await analysis_service.adjust_line_and_recalculate(
            week=request.week,
            player_name=request.player_name,
            stat_type=request.stat_type,
            bet_type=request.bet_type,
            original_line=request.original_line,
            new_line=request.new_line
        )
        return LineAdjustmentResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adjusting line: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error adjusting line: {str(e)}"
        )
