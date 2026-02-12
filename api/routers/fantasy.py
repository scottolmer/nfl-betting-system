"""
Fantasy Router — Sleeper integration, start/sit, waiver wire,
trade analysis, matchup heatmap, lineup optimization.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from api.database import get_db, Player
from api.core.jwt_auth import get_current_user
from api.services.sleeper_service import sleeper_service
from api.services.fantasy_service import fantasy_service

router = APIRouter()


# --- Pydantic Schemas ---

class SleeperConnectRequest(BaseModel):
    username: str
    season: int = 2025


class TradeAnalyzeRequest(BaseModel):
    give_player_ids: list[int]
    get_player_ids: list[int]
    week: int
    weeks_remaining: int = 4
    scoring: str = "ppr"


class OptimizeLineupRequest(BaseModel):
    player_ids: list[int]
    week: int
    scoring: str = "ppr"


# --- Sleeper Endpoints ---

@router.post("/connect-sleeper")
async def connect_sleeper(req: SleeperConnectRequest):
    """
    Connect a Sleeper account. Returns user info and their leagues.
    No auth needed from Sleeper — their API is public.
    """
    user = await sleeper_service.get_user(req.username)
    if not user:
        raise HTTPException(status_code=404, detail=f"Sleeper user '{req.username}' not found")

    leagues = await sleeper_service.get_leagues(user["user_id"], req.season)

    return {
        "user": {
            "user_id": user["user_id"],
            "username": user.get("username"),
            "display_name": user.get("display_name"),
            "avatar": user.get("avatar"),
        },
        "leagues": [
            {
                "league_id": l["league_id"],
                "name": l.get("name", "Unnamed League"),
                "total_rosters": l.get("total_rosters"),
                "scoring_settings": _detect_scoring(l),
                "status": l.get("status"),
                "season": l.get("season"),
            }
            for l in leagues
        ],
    }


@router.get("/leagues")
async def get_leagues(
    sleeper_user_id: str = Query(...),
    season: int = Query(2025),
):
    """Get all leagues for a Sleeper user."""
    leagues = await sleeper_service.get_leagues(sleeper_user_id, season)
    return [
        {
            "league_id": l["league_id"],
            "name": l.get("name", "Unnamed League"),
            "total_rosters": l.get("total_rosters"),
            "scoring_settings": _detect_scoring(l),
            "status": l.get("status"),
        }
        for l in leagues
    ]


@router.get("/roster/{league_id}")
async def get_roster(
    league_id: str,
    sleeper_user_id: str = Query(...),
    week: int = Query(17),
    scoring: str = Query("ppr"),
    db: Session = Depends(get_db),
):
    """
    Get a user's roster with fantasy point projections.
    Maps Sleeper player IDs to our Player table for engine projections.
    """
    roster = await sleeper_service.get_user_roster(league_id, sleeper_user_id)
    if not roster:
        raise HTTPException(status_code=404, detail="Roster not found for this user in league")

    sleeper_players = await sleeper_service.get_all_players()
    player_ids = roster.get("players") or []

    # Map Sleeper IDs to our DB players
    mapped_players = []
    for sid in player_ids:
        player = sleeper_service.map_sleeper_player_to_db(db, str(sid), sleeper_players)
        if player:
            mapped_players.append(player.id)

    db.commit()  # Flush any newly created players

    # Get projections for all mapped players
    projections = fantasy_service.get_roster_projections(db, mapped_players, week, scoring)

    return {
        "league_id": league_id,
        "roster_id": roster.get("roster_id"),
        "starters": roster.get("starters", []),
        "players": projections,
        "total_projected": round(sum(p["fantasy_points"] for p in projections), 1),
    }


@router.get("/start-sit/{league_id}")
async def get_start_sit(
    league_id: str,
    sleeper_user_id: str = Query(...),
    week: int = Query(17),
    position: Optional[str] = Query(None),
    scoring: str = Query("ppr"),
    db: Session = Depends(get_db),
):
    """Start/sit rankings for a user's roster."""
    roster = await sleeper_service.get_user_roster(league_id, sleeper_user_id)
    if not roster:
        raise HTTPException(status_code=404, detail="Roster not found")

    sleeper_players = await sleeper_service.get_all_players()
    player_ids = roster.get("players") or []

    mapped_ids = []
    for sid in player_ids:
        player = sleeper_service.map_sleeper_player_to_db(db, str(sid), sleeper_players)
        if player:
            mapped_ids.append(player.id)

    db.commit()

    rankings = fantasy_service.start_sit_rankings(db, mapped_ids, week, position, scoring)
    return rankings


@router.get("/waiver-wire/{league_id}")
async def get_waiver_wire(
    league_id: str,
    week: int = Query(17),
    position: Optional[str] = Query(None),
    scoring: str = Query("ppr"),
    limit: int = Query(25),
    db: Session = Depends(get_db),
):
    """
    Waiver wire rankings — best available players not on any roster in the league.
    """
    all_rosters = await sleeper_service.get_rosters(league_id)
    sleeper_players = await sleeper_service.get_all_players()

    # Collect all rostered Sleeper player IDs
    all_rostered_sids = set()
    for r in all_rosters:
        for sid in (r.get("players") or []):
            all_rostered_sids.add(str(sid))

    # Map to our DB IDs
    rostered_db_ids = []
    for sid in all_rostered_sids:
        player = sleeper_service.map_sleeper_player_to_db(db, sid, sleeper_players)
        if player:
            rostered_db_ids.append(player.id)

    db.commit()

    candidates = fantasy_service.waiver_wire_rankings(
        db, rostered_db_ids, week, position, scoring, limit
    )
    return candidates


@router.get("/matchup/{league_id}")
async def get_matchup(
    league_id: str,
    sleeper_user_id: str = Query(...),
    week: int = Query(17),
    scoring: str = Query("ppr"),
    db: Session = Depends(get_db),
):
    """
    Get matchup details: your projected total vs opponent's projected total.
    Includes player-level heatmap data.
    """
    roster = await sleeper_service.get_user_roster(league_id, sleeper_user_id)
    if not roster:
        raise HTTPException(status_code=404, detail="Roster not found")

    roster_id = roster.get("roster_id")
    opponent = await sleeper_service.get_matchup_opponent(league_id, week, roster_id)

    sleeper_players = await sleeper_service.get_all_players()

    # Map user's players
    user_player_ids = []
    for sid in (roster.get("players") or []):
        player = sleeper_service.map_sleeper_player_to_db(db, str(sid), sleeper_players)
        if player:
            user_player_ids.append(player.id)

    # Map opponent's players
    opp_player_ids = []
    if opponent:
        for sid in (opponent.get("players") or []):
            player = sleeper_service.map_sleeper_player_to_db(db, str(sid), sleeper_players)
            if player:
                opp_player_ids.append(player.id)

    db.commit()

    user_projections = fantasy_service.get_roster_projections(db, user_player_ids, week, scoring)
    opp_projections = fantasy_service.get_roster_projections(db, opp_player_ids, week, scoring)

    user_total = sum(p["fantasy_points"] for p in user_projections[:9])  # Top 9 = starters
    opp_total = sum(p["fantasy_points"] for p in opp_projections[:9])

    # Win probability estimate (simple normal approximation)
    diff = user_total - opp_total
    win_prob = min(95, max(5, 50 + diff * 2))  # Rough: each point diff = ~2% win prob

    return {
        "week": week,
        "user": {
            "roster_id": roster_id,
            "projected_total": round(user_total, 1),
            "players": user_projections[:9],
        },
        "opponent": {
            "roster_id": opponent.get("roster_id") if opponent else None,
            "projected_total": round(opp_total, 1),
            "players": opp_projections[:9],
        },
        "win_probability": round(win_prob, 1),
        "margin": round(diff, 1),
    }


@router.get("/matchup-heatmap/{league_id}")
async def get_matchup_heatmap(
    league_id: str,
    sleeper_user_id: str = Query(...),
    week: int = Query(17),
    opponent_team: str = Query(..., description="Opponent NFL team abbreviation"),
    db: Session = Depends(get_db),
):
    """
    Matchup heatmap: how each of your players matches up vs a specific defense.
    Color-coded by engine confidence (favorable/neutral/unfavorable).
    """
    roster = await sleeper_service.get_user_roster(league_id, sleeper_user_id)
    if not roster:
        raise HTTPException(status_code=404, detail="Roster not found")

    sleeper_players = await sleeper_service.get_all_players()
    player_ids = []
    for sid in (roster.get("players") or []):
        player = sleeper_service.map_sleeper_player_to_db(db, str(sid), sleeper_players)
        if player:
            player_ids.append(player.id)

    db.commit()

    heatmap = fantasy_service.matchup_heatmap(db, player_ids, opponent_team, week)
    return heatmap


@router.post("/trade-analyzer")
async def analyze_trade(
    req: TradeAnalyzeRequest,
    db: Session = Depends(get_db),
):
    """
    Analyze a trade: ROS projection comparison for give vs get players.
    Returns verdict (ACCEPT / CONSIDER / DECLINE) with reasoning.
    """
    result = fantasy_service.trade_analyzer(
        db,
        give_player_ids=req.give_player_ids,
        get_player_ids=req.get_player_ids,
        week=req.week,
        weeks_remaining=req.weeks_remaining,
        scoring=req.scoring,
    )
    return result


@router.post("/optimize-lineup")
async def optimize_lineup(
    req: OptimizeLineupRequest,
    db: Session = Depends(get_db),
):
    """
    Suggest optimal lineup from available roster players.
    Fills QB/RB/RB/WR/WR/TE/FLEX/K/DEF by highest projected points.
    """
    result = fantasy_service.optimize_lineup(
        db,
        player_ids=req.player_ids,
        week=req.week,
        scoring=req.scoring,
    )
    return result


def _detect_scoring(league: dict) -> str:
    """Detect scoring type from Sleeper league settings."""
    settings = league.get("scoring_settings", {})
    rec_pts = settings.get("rec", 0)
    if rec_pts >= 1.0:
        return "ppr"
    elif rec_pts >= 0.5:
        return "half_ppr"
    return "standard"
