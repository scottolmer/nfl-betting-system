"""
Feed Router — Unified home feed aggregating top picks from all three pillars.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from api.database import get_db, Player, PlayerProjection
from api.services.player_intel_service import player_intel_service
from api.services.game_service import game_service

router = APIRouter()


@router.get("/home")
def get_home_feed(
    week: int = Query(17),
    limit: int = Query(5),
    db: Session = Depends(get_db),
):
    """
    Aggregated home feed with top picks across all pillars.
    Returns: top prop edges, best DFS picks, fantasy alerts, game slate.
    """
    # --- Top Prop Edges ---
    top_props = db.query(PlayerProjection).filter(
        PlayerProjection.week == week,
        PlayerProjection.confidence.isnot(None),
        PlayerProjection.confidence >= 60,
    ).order_by(PlayerProjection.confidence.desc()).limit(limit).all()

    prop_edges = []
    for p in top_props:
        player = db.query(Player).filter(Player.id == p.player_id).first()
        if not player:
            continue
        prop_edges.append({
            "player_id": player.id,
            "player_name": player.name,
            "team": player.team,
            "position": player.position,
            "headshot_url": player.headshot_url,
            "stat_type": p.stat_type,
            "confidence": p.confidence,
            "direction": p.direction,
            "engine_projection": p.engine_projection,
            "implied_line": p.implied_line,
            "edge": round(p.confidence - 50, 1) if p.confidence else 0,
        })

    # --- Best DFS Picks (highest confidence with varied teams) ---
    dfs_query = db.query(PlayerProjection).filter(
        PlayerProjection.week == week,
        PlayerProjection.confidence.isnot(None),
    ).order_by(PlayerProjection.confidence.desc()).limit(limit * 3).all()

    dfs_picks = []
    seen_teams = set()
    for p in dfs_query:
        player = db.query(Player).filter(Player.id == p.player_id).first()
        if not player or player.team in seen_teams:
            continue
        seen_teams.add(player.team)
        dfs_picks.append({
            "player_id": player.id,
            "player_name": player.name,
            "team": player.team,
            "position": player.position,
            "headshot_url": player.headshot_url,
            "stat_type": p.stat_type,
            "confidence": p.confidence,
            "direction": p.direction,
        })
        if len(dfs_picks) >= limit:
            break

    # --- Fantasy Alerts (players with big edges = start candidates) ---
    fantasy_alerts = []
    big_edges = db.query(PlayerProjection).filter(
        PlayerProjection.week == week,
        PlayerProjection.confidence.isnot(None),
        PlayerProjection.confidence >= 65,
    ).order_by(PlayerProjection.confidence.desc()).limit(limit).all()

    for p in big_edges:
        player = db.query(Player).filter(Player.id == p.player_id).first()
        if not player:
            continue
        alert_type = "start" if p.direction == "OVER" else "sit"
        fantasy_alerts.append({
            "player_id": player.id,
            "player_name": player.name,
            "team": player.team,
            "position": player.position,
            "alert_type": alert_type,
            "message": f"{'Start' if alert_type == 'start' else 'Sit'} alert: {p.confidence:.0f} confidence {p.direction} on {p.stat_type}",
            "confidence": p.confidence,
        })

    # --- Game Slate ---
    slate = game_service.get_week_slate(db, week)

    return {
        "week": week,
        "sections": {
            "prop_edges": {
                "title": "Top Prop Edges",
                "subtitle": "Biggest engine edges this week",
                "items": prop_edges,
            },
            "dfs_picks": {
                "title": "DFS Highlights",
                "subtitle": "Top confidence picks for your slips",
                "items": dfs_picks,
            },
            "fantasy_alerts": {
                "title": "Fantasy Alerts",
                "subtitle": "Start/sit signals from the engine",
                "items": fantasy_alerts,
            },
            "game_slate": {
                "title": "Game Slate",
                "subtitle": f"Week {week} matchups",
                "items": slate[:8],
            },
        },
    }


@router.get("/player-intel/{player_id}")
def get_player_intelligence(
    player_id: int,
    week: int = Query(17),
    db: Session = Depends(get_db),
):
    """Full player intelligence card data."""
    intel = player_intel_service.get_full_intelligence(db, player_id, week)
    if not intel:
        return {"error": "Player not found"}
    return intel
