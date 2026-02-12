"""Bets router: save, list, update status, analytics for user bets."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from api.database import get_db, User, UserBet
from api.core.jwt_auth import get_current_user

router = APIRouter()


# --- Schemas ---

class BetLeg(BaseModel):
    player_name: str
    team: str
    position: str | None = None
    stat_type: str
    line: float
    direction: str  # OVER / UNDER
    confidence: float | None = None


class SaveBetRequest(BaseModel):
    mode: str  # dfs, props, fantasy
    platform: str | None = None
    week: int
    legs: list[BetLeg]
    confidence: float | None = None
    notes: str | None = None


class BetResponse(BaseModel):
    id: str
    mode: str
    platform: str | None
    week: int
    legs: list
    status: str
    confidence: float | None
    notes: str | None
    created_at: str | None
    updated_at: str | None

    class Config:
        from_attributes = True


class UpdateStatusRequest(BaseModel):
    status: str  # pending, placed, won, lost, push


class BetAnalyticsResponse(BaseModel):
    total_bets: int
    wins: int
    losses: int
    pushes: int
    pending: int
    win_rate: float | None
    by_mode: dict
    by_week: dict


# --- Endpoints ---

@router.post("/save", response_model=BetResponse, status_code=201)
async def save_bet(
    request: SaveBetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save a new bet to the server (replaces local storage)."""
    bet = UserBet(
        user_id=current_user.id,
        mode=request.mode,
        platform=request.platform,
        week=request.week,
        legs=[leg.model_dump() for leg in request.legs],
        confidence=request.confidence,
        notes=request.notes,
    )
    db.add(bet)
    db.commit()
    db.refresh(bet)

    return _bet_to_response(bet)


@router.get("/mine", response_model=list[BetResponse])
async def get_my_bets(
    mode: Optional[str] = None,
    week: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's bets with optional filters."""
    q = db.query(UserBet).filter(UserBet.user_id == current_user.id)
    if mode:
        q = q.filter(UserBet.mode == mode)
    if week:
        q = q.filter(UserBet.week == week)
    if status:
        q = q.filter(UserBet.status == status)

    bets = q.order_by(UserBet.created_at.desc()).limit(limit).all()
    return [_bet_to_response(b) for b in bets]


@router.put("/{bet_id}/status", response_model=BetResponse)
async def update_bet_status(
    bet_id: str,
    request: UpdateStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update the status of a bet (e.g., pending → placed → won/lost)."""
    bet = db.query(UserBet).filter(
        UserBet.id == bet_id,
        UserBet.user_id == current_user.id,
    ).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")

    valid_statuses = {"pending", "placed", "won", "lost", "push"}
    if request.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    bet.status = request.status
    db.commit()
    db.refresh(bet)
    return _bet_to_response(bet)


@router.get("/analytics", response_model=BetAnalyticsResponse)
async def get_bet_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get betting analytics for the current user."""
    bets = db.query(UserBet).filter(UserBet.user_id == current_user.id).all()

    total = len(bets)
    wins = sum(1 for b in bets if b.status == "won")
    losses = sum(1 for b in bets if b.status == "lost")
    pushes = sum(1 for b in bets if b.status == "push")
    pending = sum(1 for b in bets if b.status in ("pending", "placed"))

    decided = wins + losses
    win_rate = round((wins / decided) * 100, 1) if decided > 0 else None

    # Breakdown by mode
    by_mode: dict = {}
    for b in bets:
        if b.mode not in by_mode:
            by_mode[b.mode] = {"total": 0, "wins": 0, "losses": 0}
        by_mode[b.mode]["total"] += 1
        if b.status == "won":
            by_mode[b.mode]["wins"] += 1
        elif b.status == "lost":
            by_mode[b.mode]["losses"] += 1

    # Breakdown by week
    by_week: dict = {}
    for b in bets:
        w = str(b.week)
        if w not in by_week:
            by_week[w] = {"total": 0, "wins": 0, "losses": 0}
        by_week[w]["total"] += 1
        if b.status == "won":
            by_week[w]["wins"] += 1
        elif b.status == "lost":
            by_week[w]["losses"] += 1

    return BetAnalyticsResponse(
        total_bets=total,
        wins=wins,
        losses=losses,
        pushes=pushes,
        pending=pending,
        win_rate=win_rate,
        by_mode=by_mode,
        by_week=by_week,
    )


def _bet_to_response(bet: UserBet) -> BetResponse:
    return BetResponse(
        id=bet.id,
        mode=bet.mode,
        platform=bet.platform,
        week=bet.week,
        legs=bet.legs or [],
        status=bet.status,
        confidence=bet.confidence,
        notes=bet.notes,
        created_at=bet.created_at.isoformat() if bet.created_at else None,
        updated_at=bet.updated_at.isoformat() if bet.updated_at else None,
    )
