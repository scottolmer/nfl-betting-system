"""Odds endpoints: player odds, best prices, line movement."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from api.database import get_db, User
from api.services.odds_service import odds_service
from api.core.jwt_auth import get_current_user

router = APIRouter()


# --- Schemas ---

class BookOddsResponse(BaseModel):
    id: int
    player_id: int
    week: int
    stat_type: str
    bookmaker: str
    line: float
    over_price: int | None
    under_price: int | None
    fetched_at: str | None

    class Config:
        from_attributes = True


class BestPriceEntry(BaseModel):
    bookmaker: str
    line: float
    price: int


class BestPricesResponse(BaseModel):
    player_id: int
    stat_type: str
    best_over: BestPriceEntry | None
    best_under: BestPriceEntry | None


class LineMovementEntry(BaseModel):
    bookmaker: str
    line: float
    over_price: int | None
    under_price: int | None
    recorded_at: str | None


class FetchSummaryResponse(BaseModel):
    events: int
    total_odds: int


# --- Endpoints ---

@router.get("/player/{player_id}", response_model=list[BookOddsResponse])
async def get_player_odds(
    player_id: int,
    week: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Get all book odds for a player."""
    odds = odds_service.get_player_odds(db, player_id, week=week)
    results = []
    for o in odds:
        results.append(BookOddsResponse(
            id=o.id,
            player_id=o.player_id,
            week=o.week,
            stat_type=o.stat_type,
            bookmaker=o.bookmaker,
            line=o.line,
            over_price=o.over_price,
            under_price=o.under_price,
            fetched_at=o.fetched_at.isoformat() if o.fetched_at else None,
        ))
    return results


@router.get("/best-prices", response_model=BestPricesResponse)
async def get_best_prices(
    player_id: int = Query(...),
    stat_type: str = Query(...),
    week: int = Query(...),
    db: Session = Depends(get_db),
):
    """Find the best over/under prices across all books for a player prop."""
    result = odds_service.get_best_prices(db, player_id, stat_type, week)
    return result


@router.get("/movement/{player_id}", response_model=list[LineMovementEntry])
async def get_line_movement(
    player_id: int,
    stat_type: str = Query(...),
    week: int = Query(...),
    db: Session = Depends(get_db),
):
    """Get line movement history for a player prop."""
    return odds_service.get_line_movement(db, player_id, stat_type, week)


@router.post("/fetch-week", response_model=FetchSummaryResponse)
async def fetch_odds_for_week(
    week: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch all player prop odds from The Odds API for a week. Requires auth."""
    summary = await odds_service.fetch_all_props_for_week(db, week)
    return summary
