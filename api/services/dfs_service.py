"""
DFS service: platform line mapping, correlation scoring,
flex play optimization, and auto-generated slip suggestions.

Wraps existing CorrelationAnalyzer and ProjectionService.
"""

import logging
from typing import Optional
from sqlalchemy.orm import Session
from api.database import Player, PlayerProjection, BookOdds
from scripts.analysis.correlation_detector import CorrelationAnalyzer
from scripts.analysis.models import PropAnalysis, PlayerProp

logger = logging.getLogger(__name__)

# DFS platform-specific prop type mappings
PLATFORM_STAT_MAP = {
    "prizepicks": {
        "pass_yds": "Pass Yards",
        "rush_yds": "Rush Yards",
        "rec_yds": "Receiving Yards",
        "receptions": "Receptions",
        "pass_tds": "Pass TDs",
        "rush_rec_yds": "Rush+Rec Yards",
        "anytime_td": "Touchdowns",
    },
    "underdog": {
        "pass_yds": "Passing Yards",
        "rush_yds": "Rushing Yards",
        "rec_yds": "Receiving Yards",
        "receptions": "Receptions",
        "pass_tds": "Passing TDs",
        "rush_rec_yds": "Rush+Rec Yds",
    },
}

# Positions that can be designated as flex
FLEX_ELIGIBLE = {"RB", "WR", "TE"}


class DFSService:
    """DFS slip building, correlation scoring, and optimization."""

    def __init__(self):
        self.correlation_analyzer = CorrelationAnalyzer()

    def get_dfs_lines(
        self,
        db: Session,
        week: int,
        platform: str = "prizepicks",
        position: Optional[str] = None,
        stat_type: Optional[str] = None,
    ) -> list[dict]:
        """
        Get available DFS lines for a platform, enriched with engine projections.
        Maps our internal stat types to platform display names.
        """
        q = db.query(PlayerProjection).filter(PlayerProjection.week == week)
        if stat_type:
            q = q.filter(PlayerProjection.stat_type == stat_type)

        projections = q.all()
        stat_map = PLATFORM_STAT_MAP.get(platform.lower(), PLATFORM_STAT_MAP["prizepicks"])

        results = []
        for proj in projections:
            player = db.query(Player).filter(Player.id == proj.player_id).first()
            if not player:
                continue
            if position and player.position != position.upper():
                continue

            platform_stat = stat_map.get(proj.stat_type, proj.stat_type)

            # Get consensus line from book odds
            consensus_odds = db.query(BookOdds).filter(
                BookOdds.player_id == proj.player_id,
                BookOdds.stat_type == proj.stat_type,
                BookOdds.week == week,
            ).all()

            sportsbook_consensus = None
            if consensus_odds:
                sportsbook_consensus = round(
                    sum(o.line for o in consensus_odds) / len(consensus_odds), 1
                )

            results.append({
                "player_id": player.id,
                "player_name": player.name,
                "team": player.team,
                "position": player.position,
                "headshot_url": player.headshot_url,
                "stat_type": proj.stat_type,
                "platform_stat": platform_stat,
                "platform_line": proj.implied_line,
                "sportsbook_consensus": sportsbook_consensus,
                "engine_projection": proj.engine_projection,
                "confidence": proj.confidence,
                "direction": proj.direction,
                "agent_breakdown": proj.agent_breakdown,
            })

        results.sort(key=lambda x: x.get("confidence") or 0, reverse=True)
        return results

    def score_correlation(self, picks: list[dict]) -> dict:
        """
        Score the correlation risk of a set of DFS picks.

        Each pick should have: player_name, team, stat_type, confidence, agent_breakdown.
        Returns total penalty, per-pair warnings, and overall risk level.
        """
        # Convert picks to PropAnalysis objects for the CorrelationAnalyzer
        analyses = []
        for pick in picks:
            prop = PlayerProp(
                player_name=pick.get("player_name", ""),
                team=pick.get("team", ""),
                opponent="",
                position=pick.get("position", ""),
                stat_type=pick.get("stat_type", ""),
                line=pick.get("line", 0),
            )
            analysis = PropAnalysis(
                prop=prop,
                final_confidence=int(pick.get("confidence", 50)),
                recommendation="",
                rationale=[],
                agent_breakdown=pick.get("agent_breakdown", {}),
                edge_explanation="",
            )
            analyses.append(analysis)

        if len(analyses) < 2:
            return {
                "total_penalty": 0,
                "warnings": [],
                "risk_level": "low",
                "adjusted_confidence": self._avg_confidence(picks),
            }

        penalty, warnings = self.correlation_analyzer.analyze_parlay_correlations(analyses)

        avg_conf = self._avg_confidence(picks)
        adjusted = max(0, min(100, avg_conf + penalty))

        risk = "low" if penalty > -5 else "medium" if penalty > -10 else "high"

        return {
            "total_penalty": round(penalty, 1),
            "warnings": warnings,
            "risk_level": risk,
            "raw_confidence": round(avg_conf, 1),
            "adjusted_confidence": round(adjusted, 1),
            "pick_count": len(picks),
        }

    def optimize_flex(self, picks: list[dict]) -> dict:
        """
        Determine the optimal flex play designation for a DFS slip.

        The flex pick should be the one with:
        1. Highest confidence
        2. Lowest correlation to other picks
        3. Flex-eligible position (RB, WR, TE)

        Returns the recommended flex pick and reasoning.
        """
        flex_candidates = [
            p for p in picks if p.get("position", "").upper() in FLEX_ELIGIBLE
        ]

        if not flex_candidates:
            return {
                "flex_pick": None,
                "reason": "No flex-eligible players (RB/WR/TE) in slip",
            }

        # Score each candidate: higher confidence + lower correlation = better flex
        scored = []
        for candidate in flex_candidates:
            # Calculate correlation of this pick with the rest
            others = [p for p in picks if p.get("player_name") != candidate.get("player_name")]
            correlation_score = self._pairwise_correlation(candidate, others)
            confidence = candidate.get("confidence", 50)

            # Flex score: high confidence, low correlation
            flex_score = confidence - abs(correlation_score) * 2
            scored.append({
                **candidate,
                "flex_score": round(flex_score, 1),
                "correlation_impact": round(correlation_score, 1),
            })

        scored.sort(key=lambda x: x["flex_score"], reverse=True)
        best = scored[0]

        return {
            "flex_pick": {
                "player_name": best.get("player_name"),
                "team": best.get("team"),
                "position": best.get("position"),
                "stat_type": best.get("stat_type"),
                "flex_score": best.get("flex_score"),
            },
            "reason": (
                f"{best.get('player_name')} has the best flex score ({best['flex_score']:.0f}) — "
                f"high confidence ({best.get('confidence', 0):.0f}) with low correlation "
                f"to other picks ({best['correlation_impact']:.1f})"
            ),
            "all_candidates": scored,
        }

    def generate_suggestions(
        self,
        db: Session,
        week: int,
        platform: str = "prizepicks",
        slip_size: int = 5,
        count: int = 3,
    ) -> list[dict]:
        """
        Auto-generate optimal DFS slip suggestions.

        Strategy: pick the highest-confidence, lowest-correlation combinations.
        """
        lines = self.get_dfs_lines(db, week, platform=platform)
        # Only use picks with real confidence
        eligible = [l for l in lines if (l.get("confidence") or 0) >= 55]

        if len(eligible) < slip_size:
            return []

        suggestions = []
        used_players: set[str] = set()

        for _ in range(count):
            slip = self._build_optimal_slip(eligible, slip_size, used_players)
            if not slip:
                break

            correlation = self.score_correlation(slip)
            flex = self.optimize_flex(slip)

            suggestion = {
                "picks": slip,
                "correlation": correlation,
                "flex_recommendation": flex,
                "combined_confidence": correlation["adjusted_confidence"],
            }
            suggestions.append(suggestion)

            # Track used players to vary suggestions
            for pick in slip:
                used_players.add(pick.get("player_name", ""))

        return suggestions

    def get_line_comparison(
        self,
        db: Session,
        player_id: int,
        stat_type: str,
        week: int,
    ) -> dict:
        """
        Compare a player's DFS platform line vs sportsbook consensus.
        Highlights discrepancies where the platform line differs significantly.
        """
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return {"error": "Player not found"}

        projection = db.query(PlayerProjection).filter(
            PlayerProjection.player_id == player_id,
            PlayerProjection.stat_type == stat_type,
            PlayerProjection.week == week,
        ).first()

        book_odds = db.query(BookOdds).filter(
            BookOdds.player_id == player_id,
            BookOdds.stat_type == stat_type,
            BookOdds.week == week,
        ).all()

        books = {}
        for o in book_odds:
            books[o.bookmaker] = {"line": o.line, "over": o.over_price, "under": o.under_price}

        consensus = None
        if book_odds:
            consensus = round(sum(o.line for o in book_odds) / len(book_odds), 1)

        platform_line = projection.implied_line if projection else None
        engine_proj = projection.engine_projection if projection else None

        # Calculate discrepancy
        discrepancy = None
        if platform_line and consensus:
            discrepancy = round(platform_line - consensus, 1)

        return {
            "player_id": player_id,
            "player_name": player.name,
            "team": player.team,
            "stat_type": stat_type,
            "platform_line": platform_line,
            "sportsbook_consensus": consensus,
            "engine_projection": engine_proj,
            "discrepancy": discrepancy,
            "books": books,
            "confidence": projection.confidence if projection else None,
            "edge_note": self._discrepancy_note(discrepancy),
        }

    # --- Helpers ---

    def _avg_confidence(self, picks: list[dict]) -> float:
        confs = [p.get("confidence", 50) for p in picks]
        return sum(confs) / len(confs) if confs else 50

    def _pairwise_correlation(self, pick: dict, others: list[dict]) -> float:
        """Calculate average correlation penalty of one pick against a list of others."""
        if not others:
            return 0
        prop = PlayerProp(
            player_name=pick.get("player_name", ""), team=pick.get("team", ""),
            opponent="", position=pick.get("position", ""),
            stat_type=pick.get("stat_type", ""), line=pick.get("line", 0),
        )
        analysis = PropAnalysis(
            prop=prop, final_confidence=int(pick.get("confidence", 50)),
            recommendation="", rationale=[],
            agent_breakdown=pick.get("agent_breakdown", {}), edge_explanation="",
        )

        total = 0
        for other in others:
            other_prop = PlayerProp(
                player_name=other.get("player_name", ""), team=other.get("team", ""),
                opponent="", position=other.get("position", ""),
                stat_type=other.get("stat_type", ""), line=other.get("line", 0),
            )
            other_analysis = PropAnalysis(
                prop=other_prop, final_confidence=int(other.get("confidence", 50)),
                recommendation="", rationale=[],
                agent_breakdown=other.get("agent_breakdown", {}), edge_explanation="",
            )
            penalty, _ = self.correlation_analyzer.calculate_correlation_risk(analysis, other_analysis)
            total += penalty

        return total / len(others)

    def _build_optimal_slip(
        self, eligible: list[dict], size: int, exclude_players: set[str]
    ) -> list[dict]:
        """Greedy: pick highest-confidence players not already used, checking correlation."""
        available = [
            p for p in eligible if p.get("player_name", "") not in exclude_players
        ]
        if len(available) < size:
            return []

        slip: list[dict] = []
        for candidate in available:
            if len(slip) >= size:
                break
            # Skip duplicate players
            if candidate.get("player_name") in {p.get("player_name") for p in slip}:
                continue
            # Check correlation with current slip
            if slip:
                test_slip = slip + [candidate]
                corr = self.score_correlation(test_slip)
                if corr["risk_level"] == "high":
                    continue  # Skip high-correlation picks
            slip.append(candidate)

        return slip if len(slip) == size else []

    def _discrepancy_note(self, disc: Optional[float]) -> str:
        if disc is None:
            return "No comparison available"
        if abs(disc) < 0.5:
            return "Lines are aligned — no edge from discrepancy"
        if disc > 0:
            return f"Platform line is {disc} HIGHER than consensus — lean UNDER"
        return f"Platform line is {abs(disc)} LOWER than consensus — lean OVER"


dfs_service = DFSService()
