"""
Player Intelligence Service — Aggregates all available data for a player
into a comprehensive intelligence view.

Combines: projections, odds, agent breakdown, game environment, recent stats.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from api.database import Player, PlayerProjection, BookOdds, LineMovement
from api.services.game_service import game_service

logger = logging.getLogger(__name__)

# Stat type display labels
STAT_LABELS = {
    "pass_yds": "Pass Yards",
    "rush_yds": "Rush Yards",
    "rec_yds": "Receiving Yards",
    "receptions": "Receptions",
    "pass_tds": "Pass TDs",
    "rush_tds": "Rush TDs",
    "rec_tds": "Receiving TDs",
    "pass_attempts": "Pass Attempts",
    "completions": "Completions",
    "rush_attempts": "Rush Attempts",
    "targets": "Targets",
}


class PlayerIntelService:
    """Builds comprehensive player intelligence cards."""

    def get_full_intelligence(
        self,
        db: Session,
        player_id: int,
        week: int,
    ) -> Optional[dict]:
        """
        Aggregate all available data for a player into one intelligence payload.
        """
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return None

        # All projections for this player/week
        projections = db.query(PlayerProjection).filter(
            PlayerProjection.player_id == player_id,
            PlayerProjection.week == week,
        ).all()

        # All odds for this player/week
        all_odds = db.query(BookOdds).filter(
            BookOdds.player_id == player_id,
            BookOdds.week == week,
        ).all()

        # Line movement
        movements = db.query(LineMovement).filter(
            LineMovement.player_id == player_id,
            LineMovement.week == week,
        ).order_by(LineMovement.recorded_at.asc()).all()

        # Build stat projections
        stat_projections = []
        primary_confidence = None
        primary_direction = None

        for proj in projections:
            stat_odds = [o for o in all_odds if o.stat_type == proj.stat_type]
            books = {}
            for o in stat_odds:
                books[o.bookmaker] = {
                    "line": o.line,
                    "over_price": o.over_price,
                    "under_price": o.under_price,
                }

            consensus_line = None
            if stat_odds:
                consensus_line = round(sum(o.line for o in stat_odds) / len(stat_odds), 1)

            # Line movement for this stat
            stat_movements = [
                {"line": m.line, "recorded_at": m.recorded_at.isoformat()}
                for m in movements
                if m.stat_type == proj.stat_type
            ]

            entry = {
                "stat_type": proj.stat_type,
                "stat_label": STAT_LABELS.get(proj.stat_type, proj.stat_type),
                "engine_projection": proj.engine_projection,
                "implied_line": proj.implied_line,
                "consensus_line": consensus_line,
                "confidence": proj.confidence,
                "direction": proj.direction,
                "agent_breakdown": proj.agent_breakdown or {},
                "book_count": len(stat_odds),
                "books": books,
                "line_movement": stat_movements,
            }
            stat_projections.append(entry)

            # Track the highest-confidence stat as primary
            if proj.confidence and (primary_confidence is None or proj.confidence > primary_confidence):
                primary_confidence = proj.confidence
                primary_direction = proj.direction

        # Sort by confidence descending
        stat_projections.sort(
            key=lambda s: s.get("confidence") or 0, reverse=True
        )

        # Top agent drivers (from highest-confidence projection)
        top_drivers = []
        if stat_projections and stat_projections[0].get("agent_breakdown"):
            breakdown = stat_projections[0]["agent_breakdown"]
            drivers = []
            for name, data in breakdown.items():
                score = data.get("score", 50) if isinstance(data, dict) else 50
                weight = data.get("weight", 1) if isinstance(data, dict) else 1
                direction = data.get("direction", "NEUTRAL") if isinstance(data, dict) else "NEUTRAL"
                impact = weight * abs(score - 50)
                drivers.append({
                    "agent": name,
                    "score": score,
                    "weight": weight,
                    "direction": direction,
                    "impact": round(impact, 1),
                })
            drivers.sort(key=lambda d: d["impact"], reverse=True)
            top_drivers = drivers[:3]

        # Game environment
        game_env = game_service.get_game_environment(
            db, player.team, "OPP", week
        )

        return {
            "player": {
                "id": player.id,
                "name": player.name,
                "team": player.team,
                "position": player.position,
                "headshot_url": player.headshot_url,
                "status": player.status,
            },
            "week": week,
            "primary_confidence": primary_confidence,
            "primary_direction": primary_direction,
            "stat_projections": stat_projections,
            "top_drivers": top_drivers,
            "game_environment": game_env,
            "total_book_count": len(set(o.bookmaker for o in all_odds)),
        }

    def get_player_summary(
        self,
        db: Session,
        player_id: int,
        week: int,
    ) -> Optional[dict]:
        """Lightweight summary for feed cards (no full odds/movement data)."""
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return None

        projections = db.query(PlayerProjection).filter(
            PlayerProjection.player_id == player_id,
            PlayerProjection.week == week,
            PlayerProjection.confidence.isnot(None),
        ).order_by(PlayerProjection.confidence.desc()).all()

        if not projections:
            return None

        top = projections[0]
        return {
            "player_id": player.id,
            "player_name": player.name,
            "team": player.team,
            "position": player.position,
            "headshot_url": player.headshot_url,
            "stat_type": top.stat_type,
            "stat_label": STAT_LABELS.get(top.stat_type, top.stat_type),
            "engine_projection": top.engine_projection,
            "implied_line": top.implied_line,
            "confidence": top.confidence,
            "direction": top.direction,
        }


player_intel_service = PlayerIntelService()
