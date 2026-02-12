"""Player endpoints: search, details, projections, roster sync."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from api.database import get_db
from api.services.player_service import player_service
from api.core.jwt_auth import get_current_user, get_optional_user
from api.database import User

router = APIRouter()


# --- Schemas ---

class PlayerResponse(BaseModel):
    id: int
    name: str
    team: str
    position: str
    espn_id: str | None
    headshot_url: str | None
    status: str | None

    class Config:
        from_attributes = True


class ProjectionResponse(BaseModel):
    id: int
    player_id: int
    week: int
    stat_type: str
    implied_line: float | None
    engine_projection: float | None
    confidence: float | None
    direction: str | None
    agent_breakdown: dict | None

    class Config:
        from_attributes = True


class RosterSyncResponse(BaseModel):
    team: str
    players_synced: int


# --- Endpoints ---

@router.get("/search", response_model=list[PlayerResponse])
async def search_players(
    q: str = Query(..., min_length=2, description="Search query"),
    position: Optional[str] = None,
    team: Optional[str] = None,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
):
    """Search players by name. No auth required."""
    players = player_service.search(db, q, position=position, team=team, limit=limit)
    return players


@router.get("/{player_id}", response_model=PlayerResponse)
async def get_player(player_id: int, db: Session = Depends(get_db)):
    """Get player details by ID."""
    player = player_service.get_by_id(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.get("/{player_id}/projections", response_model=list[ProjectionResponse])
async def get_player_projections(
    player_id: int,
    week: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get projections for a player, optionally filtered by week."""
    player = player_service.get_by_id(db, player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    projections = player_service.get_projections(db, player_id, week=week)
    return projections


@router.post("/sync/{team_abbr}", response_model=RosterSyncResponse)
async def sync_team_roster(
    team_abbr: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sync a team's roster from ESPN. Requires auth."""
    count = await player_service.sync_team_roster(db, team_abbr.upper())
    return RosterSyncResponse(team=team_abbr.upper(), players_synced=count)


@router.post("/sync-all", response_model=list[RosterSyncResponse])
async def sync_all_rosters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sync all 32 NFL team rosters from ESPN. Requires auth."""
    results = await player_service.sync_all_rosters(db)
    return [RosterSyncResponse(team=t, players_synced=c) for t, c in results.items()]
