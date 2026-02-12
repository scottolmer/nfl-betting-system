"""DFS router: lines, correlation scoring, flex optimization, suggestions, line comparison."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from api.database import get_db
from api.dependencies import get_api_key
from api.services.dfs_service import dfs_service

router = APIRouter()


# --- Schemas ---

class DFSPick(BaseModel):
    player_name: str
    team: str
    position: str | None = None
    stat_type: str
    line: float = 0
    confidence: float = 50
    agent_breakdown: dict | None = None


class CorrelationRequest(BaseModel):
    picks: list[DFSPick]


class FlexRequest(BaseModel):
    picks: list[DFSPick]


# --- Endpoints ---

@router.get("/lines")
async def get_dfs_lines(
    week: int = Query(..., ge=1, le=18),
    platform: str = Query("prizepicks"),
    position: Optional[str] = None,
    stat_type: Optional[str] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    """Get available DFS lines enriched with engine projections."""
    return dfs_service.get_dfs_lines(
        db, week, platform=platform, position=position, stat_type=stat_type,
    )


@router.post("/correlation-score")
async def score_correlation(
    request: CorrelationRequest,
    api_key: str = Depends(get_api_key),
):
    """Score the correlation risk of a set of DFS picks."""
    picks = [p.model_dump() for p in request.picks]
    return dfs_service.score_correlation(picks)


@router.post("/optimize-flex")
async def optimize_flex(
    request: FlexRequest,
    api_key: str = Depends(get_api_key),
):
    """Determine optimal flex play designation for a DFS slip."""
    picks = [p.model_dump() for p in request.picks]
    return dfs_service.optimize_flex(picks)


@router.get("/suggestions")
async def get_suggestions(
    week: int = Query(..., ge=1, le=18),
    platform: str = Query("prizepicks"),
    slip_size: int = Query(5, ge=2, le=8),
    count: int = Query(3, ge=1, le=5),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    """Get auto-generated optimal DFS slip suggestions."""
    return dfs_service.generate_suggestions(
        db, week, platform=platform, slip_size=slip_size, count=count,
    )


@router.get("/line-comparison/{player_id}")
async def get_line_comparison(
    player_id: int,
    stat_type: str = Query(...),
    week: int = Query(..., ge=1, le=18),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
    """Compare platform line vs sportsbook consensus for a player."""
    result = dfs_service.get_line_comparison(db, player_id, stat_type, week)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
