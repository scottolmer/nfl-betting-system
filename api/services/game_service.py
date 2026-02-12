"""
Game Service — Game environment context: implied total, spread, pace, pass/run balance.

Derives game-level context from odds data to enrich player-level analysis.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from api.database import BookOdds, Player, PlayerProjection

logger = logging.getLogger(__name__)

# NFL team abbreviation → division mapping for rivalry detection
DIVISIONS = {
    "NFC East": ["DAL", "NYG", "PHI", "WAS"],
    "NFC North": ["CHI", "DET", "GB", "MIN"],
    "NFC South": ["ATL", "CAR", "NO", "TB"],
    "NFC West": ["ARI", "LAR", "SF", "SEA"],
    "AFC East": ["BUF", "MIA", "NE", "NYJ"],
    "AFC North": ["BAL", "CIN", "CLE", "PIT"],
    "AFC South": ["HOU", "IND", "JAX", "TEN"],
    "AFC West": ["DEN", "KC", "LV", "LAC"],
}

# Teams with domed stadiums
DOME_TEAMS = {"ARI", "ATL", "DAL", "DET", "HOU", "IND", "LV", "MIN", "NO", "LAR", "LAC"}

# Pace tier by team (fast/avg/slow) — simplified static model
PACE_TIERS = {
    "fast": ["MIA", "BUF", "LAR", "DET", "PHI", "SF"],
    "slow": ["BAL", "TEN", "NYJ", "CLE", "DEN", "PIT"],
}


class GameService:
    """Provides game-level environment context for analysis."""

    def get_game_environment(
        self,
        db: Session,
        home_team: str,
        away_team: str,
        week: int,
    ) -> dict:
        """
        Build game environment from available data.
        Uses player prop totals as a proxy for implied game total when
        game-level odds aren't directly stored.
        """
        # Estimate implied total from player projection data
        implied_total = self._estimate_implied_total(db, home_team, away_team, week)
        spread = self._estimate_spread(db, home_team, away_team, week)

        # Determine pace
        pace = self._get_pace_tier(home_team, away_team)

        # Dome/outdoor
        dome = home_team in DOME_TEAMS

        # Pass/run balance estimate based on implied total
        pass_pct = 58  # League average
        if implied_total and implied_total > 50:
            pass_pct = 62  # High-scoring = more passing
        elif implied_total and implied_total < 40:
            pass_pct = 54  # Low-scoring = more running

        # Division rivalry flag
        is_rivalry = self._is_division_game(home_team, away_team)

        return {
            "home_team": home_team,
            "away_team": away_team,
            "week": week,
            "implied_total": implied_total,
            "spread": spread,
            "spread_favor": home_team if spread and spread < 0 else away_team,
            "pace": pace,
            "dome": dome,
            "pass_pct": pass_pct,
            "run_pct": 100 - pass_pct,
            "is_division_game": is_rivalry,
        }

    def get_week_slate(self, db: Session, week: int) -> list[dict]:
        """
        Build the full slate of games for a week.
        Identifies unique team matchups from player projections.
        """
        # Get all teams with projections this week
        team_query = db.query(Player.team).join(PlayerProjection).filter(
            PlayerProjection.week == week,
        ).distinct().all()

        teams = [t[0] for t in team_query if t[0]]

        # Simple matchup detection: pair teams by their game (we don't have a games table,
        # so we approximate from the player data)
        games = []
        seen_teams = set()

        for team in sorted(teams):
            if team in seen_teams:
                continue

            # Find opponent by looking at matchup data in projections
            # For now, build a simple slate entry per team
            env = self.get_game_environment(db, team, "OPP", week)
            games.append({
                "home_team": team,
                "implied_total": env["implied_total"],
                "pace": env["pace"],
                "dome": env["dome"],
            })
            seen_teams.add(team)

        # Sort by implied total descending (most interesting games first)
        games.sort(key=lambda g: g.get("implied_total") or 0, reverse=True)
        return games

    def _estimate_implied_total(
        self, db: Session, home_team: str, away_team: str, week: int
    ) -> Optional[float]:
        """Estimate game total from player passing yard projections."""
        # Sum QB passing projections as a proxy
        for team in [home_team, away_team]:
            qb_projs = db.query(PlayerProjection).join(Player).filter(
                Player.team == team,
                Player.position == "QB",
                PlayerProjection.week == week,
                PlayerProjection.stat_type == "pass_yds",
            ).all()

            if qb_projs:
                # Convert passing yards to approximate points (1 TD per ~40 yds)
                total_pass_yds = sum(p.engine_projection or 0 for p in qb_projs)
                # Rough: each team scores ~(pass_yds / 40) TDs from passing
                # Plus rushing and other scoring ≈ 1.3x multiplier
                estimated_pts = (total_pass_yds / 40) * 7 * 1.3
                return round(estimated_pts * 2 / 7 * 7, 1)  # Both teams, round to nearest

        return None

    def _estimate_spread(
        self, db: Session, home_team: str, away_team: str, week: int
    ) -> Optional[float]:
        """Estimate spread from relative QB projection quality."""
        home_conf = self._get_team_avg_confidence(db, home_team, week)
        away_conf = self._get_team_avg_confidence(db, away_team, week)

        if home_conf and away_conf:
            diff = (home_conf - away_conf) / 5  # Scale to spread-like range
            return round(diff * -1, 1)  # Negative = home favored

        return None

    def _get_team_avg_confidence(
        self, db: Session, team: str, week: int
    ) -> Optional[float]:
        """Average engine confidence for a team's players."""
        projs = db.query(PlayerProjection).join(Player).filter(
            Player.team == team,
            PlayerProjection.week == week,
            PlayerProjection.confidence.isnot(None),
        ).all()

        if projs:
            return sum(p.confidence for p in projs) / len(projs)
        return None

    def _get_pace_tier(self, team1: str, team2: str) -> str:
        """Determine combined pace tier for a matchup."""
        fast = PACE_TIERS.get("fast", [])
        slow = PACE_TIERS.get("slow", [])

        fast_count = (team1 in fast) + (team2 in fast)
        slow_count = (team1 in slow) + (team2 in slow)

        if fast_count >= 1 and slow_count == 0:
            return "fast"
        elif slow_count >= 1 and fast_count == 0:
            return "slow"
        return "average"

    def _is_division_game(self, team1: str, team2: str) -> bool:
        """Check if two teams are in the same division."""
        for teams in DIVISIONS.values():
            if team1 in teams and team2 in teams:
                return True
        return False


game_service = GameService()
