"""Props analysis API endpoints"""

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from api.dependencies import get_api_key
from api.services.analysis_service import AnalysisService
from api.services.edge_service import edge_service
from api.schemas.props import PropAnalysisResponse
from api.schemas.line_adjustment import LineAdjustmentRequest, LineAdjustmentResponse
from api.database import get_db
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


@router.get(
    "/edge-finder",
    summary="Find biggest edges across all props",
    description="Compare engine confidence vs implied probability to find the largest edges.",
)
async def edge_finder(
    week: int = Query(..., ge=1, le=18),
    min_edge: float = Query(2.0, description="Minimum edge percentage"),
    min_confidence: float = Query(55.0, description="Minimum engine confidence"),
    limit: int = Query(30, le=100),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    """Find the biggest edges between engine confidence and market odds."""
    try:
        edges = edge_service.find_edges(
            db, week,
            min_edge=min_edge,
            min_confidence=min_confidence,
            limit=limit,
        )
        return edges
    except Exception as e:
        logger.error(f"Edge finder error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/bet-sizing",
    summary="Get bet sizing recommendation",
    description="Kelly Criterion-based bet sizing for a specific prop.",
)
async def bet_sizing(
    confidence: float = Query(..., ge=0, le=100, description="Engine confidence (0-100)"),
    american_odds: int = Query(..., description="American odds (e.g. -110, +150)"),
    bankroll: float = Query(100.0, description="Bankroll in units"),
    api_key: str = Depends(get_api_key),
):
    """Calculate bet sizing based on Kelly Criterion."""
    return edge_service.get_bet_sizing(confidence, american_odds, bankroll)


@router.get(
    "/player-history",
    summary="Get historical stat values for a player",
    description="Returns game-by-game stat values for a player and stat type across recent weeks.",
)
async def get_player_history(
    player_name: str = Query(..., description="Player name (e.g., 'Patrick Mahomes')"),
    stat_type: str = Query(..., description="Stat type (e.g., 'Pass Yds', 'Rush Yds', 'Rec Yds', 'Receptions')"),
    week: int = Query(..., ge=1, le=18, description="Current NFL week (history loaded from preceding weeks)"),
    line: Optional[float] = Query(None, description="Betting line to calculate hit rate against"),
    api_key: str = Depends(get_api_key),
):
    """
    Get a player's historical stat values from recent weeks.
    Returns structured data for hit rate bars, sparklines, and trend charts.
    """
    import re
    import pandas as pd

    # Map stat types to one or more (data_file, column_name) tuples
    stat_mapping = {
        'Receptions': [('receiving_base', 'REC')],
        'Rec Yds': [('receiving_base', 'YDS')],
        'Rush Yds': [('rushing_base', 'YDS')],
        'Rush Att': [('rushing_base', 'ATT')],
        'Rush Attempts': [('rushing_base', 'ATT')],
        'Pass Yds': [('passing_base', 'YDS')],
        'Completions': [('passing_base', 'COM')],
        'Pass Completions': [('passing_base', 'COM')],
        'Pass Att': [('passing_base', 'ATT')],
        'Pass Attempts': [('passing_base', 'ATT')],
        'Pass TDs': [('passing_base', 'TD')],
        'Rush TDs': [('rushing_base', 'TD')],
        'Rec TDs': [('receiving_base', 'TD')],
        # Composite stats
        'Rush+Rec Yds': [('rushing_base', 'YDS'), ('receiving_base', 'YDS')],
        'Pass+Rush Yds': [('passing_base', 'YDS'), ('rushing_base', 'YDS')],
    }

    stat_components = stat_mapping.get(stat_type)
    if not stat_components:
        return {"values": [], "average": None, "message": f"Stat type '{stat_type}' not supported for history"}

    try:
        # Load data using the analysis service's loader
        context = analysis_service.loader.load_all_data(week=week)
        historical_stats = context.get('historical_stats', {})

        player_name_lower = re.sub(r'\s+', ' ', player_name.lower().strip())
        weekly_values = []

        # Iterate through weeks ensuring specific order
        for week_key in sorted(historical_stats.keys()):
            week_data = historical_stats[week_key]
            
            week_total = 0.0
            found_any = False
            
            # For each component of the stat (e.g., [Rush Yds, Rec Yds])
            for data_file, column_name in stat_components:
                if data_file not in week_data:
                    continue

                df = week_data[data_file]
                if 'Player_Normalized' not in df.columns:
                    df['Player_Normalized'] = df['Player'].str.lower().str.strip().str.replace(r'\s+', ' ', regex=True)
                
                player_row = df[df['Player_Normalized'] == player_name_lower]

                if not player_row.empty and column_name in player_row.columns:
                    val = player_row.iloc[0][column_name]
                    try:
                        week_total += float(val)
                        found_any = True
                    except (ValueError, TypeError):
                        pass
            
            # Only add if we found data in at least one of the files
            if found_any:
                weekly_values.append(week_total)

        if not weekly_values:
            return {"values": [], "average": None, "message": "No historical data found for this player/stat"}

        avg = sum(weekly_values) / len(weekly_values)
        result = {
            "values": weekly_values,
            "average": round(avg, 1),
            "total_games": len(weekly_values),
        }

        if line is not None:
            over_count = sum(1 for v in weekly_values if v > line)
            under_count = sum(1 for v in weekly_values if v < line)
            result["line"] = line
            result["over_count"] = over_count
            result["under_count"] = under_count
            result["hit_rate_pct"] = round((over_count / len(weekly_values)) * 100, 1)

        return result

    except Exception as e:
        logger.error(f"Error getting player history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/odds",
    summary="Get raw betting odds for a player",
    description="Get odds from raw betting lines CSV for a specific player and stat type."
)
async def get_player_odds_endpoint(
    week: int = Query(..., ge=1, le=18),
    player_name: str = Query(...),
    stat_type: str = Query(...),
    api_key: str = Depends(get_api_key)
):
    """
    Get raw betting odds for a player/stat from the loaded CSVs.
    Useful for displaying live odds comparison on the frontend.
    """
    try:
        odds = analysis_service.get_player_odds(week, player_name, stat_type)
        return odds
    except Exception as e:
        logger.error(f"Error getting player odds: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
