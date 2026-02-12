"""
Fantasy Service — Start/sit rankings, waiver wire, trade analysis,
matchup heatmaps, and projection → fantasy points conversion.

Consumes the same ProjectionService that powers DFS and Props modes.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from api.database import Player, PlayerProjection
from api.services.sleeper_service import sleeper_service

logger = logging.getLogger(__name__)

# Standard fantasy scoring (PPR)
SCORING_PPR = {
    "pass_yds": 0.04,       # 1 pt per 25 yards
    "pass_tds": 4.0,
    "interceptions": -2.0,
    "rush_yds": 0.1,        # 1 pt per 10 yards
    "rush_tds": 6.0,
    "receptions": 1.0,      # PPR
    "rec_yds": 0.1,
    "rec_tds": 6.0,
}

# Half-PPR variant
SCORING_HALF_PPR = {**SCORING_PPR, "receptions": 0.5}

# Standard (no PPR)
SCORING_STANDARD = {**SCORING_PPR, "receptions": 0.0}

SCORING_PRESETS = {
    "ppr": SCORING_PPR,
    "half_ppr": SCORING_HALF_PPR,
    "standard": SCORING_STANDARD,
}

# Position slots for typical fantasy league
ROSTER_SLOTS = ["QB", "RB", "RB", "WR", "WR", "TE", "FLEX", "K", "DEF"]

# DVOA position matchup quality (lower = easier matchup)
# These would ideally come from live DVOA data, but we use engine projections as proxy
POSITION_GROUPS = {
    "QB": ["pass_yds", "pass_tds"],
    "RB": ["rush_yds", "rush_tds", "receptions", "rec_yds"],
    "WR": ["receptions", "rec_yds", "rec_tds"],
    "TE": ["receptions", "rec_yds", "rec_tds"],
}


class FantasyService:
    """Fantasy analysis powered by the same projection engine as DFS/Props."""

    def projection_to_fantasy_points(
        self, projections: list[dict], scoring: str = "ppr"
    ) -> float:
        """
        Convert stat projections to fantasy points.
        projections: list of {stat_type, engine_projection} dicts
        """
        weights = SCORING_PRESETS.get(scoring, SCORING_PPR)
        total = 0.0
        for proj in projections:
            stat = proj.get("stat_type", "")
            value = proj.get("engine_projection") or 0
            if stat in weights:
                total += value * weights[stat]
        return round(total, 1)

    def get_player_fantasy_projection(
        self, db: Session, player_id: int, week: int, scoring: str = "ppr"
    ) -> dict:
        """Get a player's fantasy point projection for a week."""
        projections = db.query(PlayerProjection).filter(
            PlayerProjection.player_id == player_id,
            PlayerProjection.week == week,
        ).all()

        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"player_id": player_id, "fantasy_points": 0, "projections": []}

        proj_list = []
        for p in projections:
            proj_list.append({
                "stat_type": p.stat_type,
                "engine_projection": p.engine_projection,
                "confidence": p.confidence,
                "direction": p.direction,
            })

        fp = self.projection_to_fantasy_points(proj_list, scoring)

        # Calculate floor/ceiling based on confidence spread
        confidences = [p.confidence for p in projections if p.confidence]
        avg_conf = sum(confidences) / len(confidences) if confidences else 50
        spread = max(0.15, (100 - avg_conf) / 100 * 0.35)  # Higher conf = tighter range
        floor_pts = round(fp * (1 - spread), 1)
        ceiling_pts = round(fp * (1 + spread), 1)

        return {
            "player_id": player_id,
            "player_name": player.name,
            "team": player.team,
            "position": player.position,
            "headshot_url": player.headshot_url,
            "fantasy_points": fp,
            "floor": floor_pts,
            "ceiling": ceiling_pts,
            "confidence": round(avg_conf, 1),
            "projections": proj_list,
        }

    def get_roster_projections(
        self,
        db: Session,
        player_ids: list[int],
        week: int,
        scoring: str = "ppr",
    ) -> list[dict]:
        """Get fantasy projections for an entire roster."""
        results = []
        for pid in player_ids:
            proj = self.get_player_fantasy_projection(db, pid, week, scoring)
            if proj["fantasy_points"] > 0:
                results.append(proj)
        results.sort(key=lambda x: x["fantasy_points"], reverse=True)
        return results

    def start_sit_rankings(
        self,
        db: Session,
        player_ids: list[int],
        week: int,
        position: Optional[str] = None,
        scoring: str = "ppr",
    ) -> dict:
        """
        Generate start/sit rankings for a roster.
        Returns players sorted by fantasy points with start/sit/flex designation.
        """
        projections = self.get_roster_projections(db, player_ids, week, scoring)

        if position:
            projections = [p for p in projections if p["position"] == position]

        # Determine start/sit thresholds by position
        by_position: dict[str, list] = {}
        for p in projections:
            pos = p["position"]
            by_position.setdefault(pos, []).append(p)

        # Standard starter counts
        starter_counts = {"QB": 1, "RB": 2, "WR": 2, "TE": 1}

        rankings = []
        for pos, players in by_position.items():
            players.sort(key=lambda x: x["fantasy_points"], reverse=True)
            starters = starter_counts.get(pos, 1)
            for i, p in enumerate(players):
                verdict = "START" if i < starters else "SIT"
                # Borderline cases: close to the starter threshold
                if i == starters and len(players) > starters:
                    prev_pts = players[i - 1]["fantasy_points"]
                    if prev_pts - p["fantasy_points"] < 2.0:
                        verdict = "FLEX"
                rankings.append({
                    **p,
                    "rank": i + 1,
                    "verdict": verdict,
                    "reason": self._start_sit_reason(p, verdict),
                })

        rankings.sort(key=lambda x: x["fantasy_points"], reverse=True)
        return {"week": week, "scoring": scoring, "rankings": rankings}

    def _start_sit_reason(self, projection: dict, verdict: str) -> str:
        """Generate a human-readable start/sit reason."""
        fp = projection["fantasy_points"]
        conf = projection.get("confidence", 50)
        name = projection["player_name"]

        if verdict == "START":
            if conf >= 65:
                return f"High-confidence projection of {fp} pts. Engine likes this matchup."
            return f"Projected {fp} pts. Reliable floor makes {name} a solid start."
        elif verdict == "FLEX":
            return f"Borderline at {fp} pts. Consider matchup and ceiling upside."
        else:
            if conf < 45:
                return f"Low confidence ({conf:.0f}). Projected only {fp} pts — better options likely available."
            return f"Projected {fp} pts. Below starter threshold for this position."

    def waiver_wire_rankings(
        self,
        db: Session,
        rostered_player_ids: list[int],
        week: int,
        position: Optional[str] = None,
        scoring: str = "ppr",
        limit: int = 25,
    ) -> list[dict]:
        """
        Find best available players not on the user's roster.
        Queries all projections for the week, excludes rostered players.
        """
        query = db.query(PlayerProjection).filter(
            PlayerProjection.week == week,
            PlayerProjection.confidence.isnot(None),
        )

        if rostered_player_ids:
            query = query.filter(~PlayerProjection.player_id.in_(rostered_player_ids))

        all_projections = query.all()

        # Group by player
        by_player: dict[int, list] = {}
        for p in all_projections:
            by_player.setdefault(p.player_id, []).append(p)

        candidates = []
        for pid, projs in by_player.items():
            player = db.query(Player).filter(Player.id == pid).first()
            if not player:
                continue
            if position and player.position != position:
                continue

            proj_list = [{
                "stat_type": p.stat_type,
                "engine_projection": p.engine_projection,
                "confidence": p.confidence,
            } for p in projs]

            fp = self.projection_to_fantasy_points(proj_list, scoring)
            if fp <= 0:
                continue

            avg_conf = sum(p.confidence for p in projs if p.confidence) / max(len([p for p in projs if p.confidence]), 1)

            candidates.append({
                "player_id": pid,
                "player_name": player.name,
                "team": player.team,
                "position": player.position,
                "headshot_url": player.headshot_url,
                "fantasy_points": fp,
                "confidence": round(avg_conf, 1),
                "waiver_score": round(fp * (avg_conf / 50), 1),  # Weight by confidence
            })

        candidates.sort(key=lambda x: x["waiver_score"], reverse=True)
        return candidates[:limit]

    def trade_analyzer(
        self,
        db: Session,
        give_player_ids: list[int],
        get_player_ids: list[int],
        week: int,
        weeks_remaining: int = 4,
        scoring: str = "ppr",
    ) -> dict:
        """
        Analyze a trade: compare ROS (rest of season) projected value.
        """
        give_total = 0.0
        give_players = []
        for pid in give_player_ids:
            proj = self.get_player_fantasy_projection(db, pid, week, scoring)
            ros_value = proj["fantasy_points"] * weeks_remaining
            give_total += ros_value
            give_players.append({**proj, "ros_value": round(ros_value, 1)})

        get_total = 0.0
        get_players = []
        for pid in get_player_ids:
            proj = self.get_player_fantasy_projection(db, pid, week, scoring)
            ros_value = proj["fantasy_points"] * weeks_remaining
            get_total += ros_value
            get_players.append({**proj, "ros_value": round(ros_value, 1)})

        diff = get_total - give_total
        diff_pct = (diff / give_total * 100) if give_total > 0 else 0

        if diff_pct > 10:
            verdict = "ACCEPT"
            verdict_reason = f"You gain {diff:.1f} projected ROS points ({diff_pct:+.1f}%). Clear win."
        elif diff_pct > -5:
            verdict = "CONSIDER"
            verdict_reason = f"Roughly even trade ({diff_pct:+.1f}%). Consider positional need."
        else:
            verdict = "DECLINE"
            verdict_reason = f"You lose {abs(diff):.1f} projected ROS points ({diff_pct:+.1f}%). Bad value."

        return {
            "give": give_players,
            "get": get_players,
            "give_ros_total": round(give_total, 1),
            "get_ros_total": round(get_total, 1),
            "ros_diff": round(diff, 1),
            "ros_diff_pct": round(diff_pct, 1),
            "verdict": verdict,
            "verdict_reason": verdict_reason,
            "weeks_remaining": weeks_remaining,
            "scoring": scoring,
        }

    def matchup_heatmap(
        self,
        db: Session,
        player_ids: list[int],
        opponent_team: str,
        week: int,
    ) -> list[dict]:
        """
        Build a matchup heatmap: each player's projections vs the opponent defense.
        Uses confidence as a proxy for matchup quality (higher = better matchup).
        """
        heatmap = []
        for pid in player_ids:
            player = db.query(Player).filter(Player.id == pid).first()
            if not player:
                continue

            projections = db.query(PlayerProjection).filter(
                PlayerProjection.player_id == pid,
                PlayerProjection.week == week,
            ).all()

            stat_matchups = []
            for p in projections:
                # Confidence indicates how favorable the matchup is
                # High confidence OVER = good matchup; high confidence UNDER = bad matchup
                matchup_grade = "neutral"
                color_value = 50  # 0=worst, 100=best
                if p.confidence and p.direction:
                    if p.direction == "OVER" and p.confidence >= 60:
                        matchup_grade = "favorable"
                        color_value = min(100, p.confidence)
                    elif p.direction == "OVER" and p.confidence >= 50:
                        matchup_grade = "neutral"
                        color_value = 50
                    elif p.direction == "UNDER" or (p.confidence and p.confidence < 45):
                        matchup_grade = "unfavorable"
                        color_value = max(0, 100 - p.confidence if p.confidence else 30)

                stat_matchups.append({
                    "stat_type": p.stat_type,
                    "projection": p.engine_projection,
                    "confidence": p.confidence,
                    "matchup_grade": matchup_grade,
                    "color_value": color_value,
                })

            if stat_matchups:
                avg_color = sum(s["color_value"] for s in stat_matchups) / len(stat_matchups)
                heatmap.append({
                    "player_id": pid,
                    "player_name": player.name,
                    "team": player.team,
                    "position": player.position,
                    "opponent": opponent_team,
                    "overall_grade": "favorable" if avg_color >= 60 else "unfavorable" if avg_color < 40 else "neutral",
                    "overall_color_value": round(avg_color),
                    "stat_matchups": stat_matchups,
                })

        return heatmap

    def optimize_lineup(
        self,
        db: Session,
        player_ids: list[int],
        week: int,
        scoring: str = "ppr",
        roster_slots: Optional[list[str]] = None,
    ) -> dict:
        """
        Suggest optimal lineup from available roster players.
        Fills each roster slot with the highest-projected eligible player.
        """
        slots = roster_slots or ROSTER_SLOTS
        projections = self.get_roster_projections(db, player_ids, week, scoring)

        # Build eligible players per slot
        position_eligible = {
            "QB": ["QB"],
            "RB": ["RB"],
            "WR": ["WR"],
            "TE": ["TE"],
            "FLEX": ["RB", "WR", "TE"],
            "K": ["K"],
            "DEF": ["DEF"],
        }

        lineup = []
        used_ids = set()
        bench = []

        for slot in slots:
            eligible_positions = position_eligible.get(slot, [slot])
            candidates = [
                p for p in projections
                if p["position"] in eligible_positions and p["player_id"] not in used_ids
            ]
            if candidates:
                best = candidates[0]  # Already sorted by fantasy_points desc
                lineup.append({**best, "slot": slot})
                used_ids.add(best["player_id"])

        # Everyone else is bench
        for p in projections:
            if p["player_id"] not in used_ids:
                bench.append({**p, "slot": "BN"})

        total_pts = sum(p["fantasy_points"] for p in lineup)

        return {
            "lineup": lineup,
            "bench": bench,
            "projected_total": round(total_pts, 1),
            "scoring": scoring,
        }


fantasy_service = FantasyService()
