"""
Edge service: compare agent confidence vs implied probability,
Kelly-based bet sizing, and edge detection across all props.
"""

import math
import logging
from typing import Optional
from sqlalchemy.orm import Session
from api.database import Player, PlayerProjection, BookOdds

logger = logging.getLogger(__name__)


def american_to_implied_prob(american_odds: int) -> float:
    """Convert American odds to implied probability (0-1)."""
    if american_odds > 0:
        return 100.0 / (american_odds + 100)
    else:
        return abs(american_odds) / (abs(american_odds) + 100)


def american_to_decimal(american_odds: int) -> float:
    """Convert American odds to decimal odds."""
    if american_odds > 0:
        return (american_odds / 100) + 1
    else:
        return (100 / abs(american_odds)) + 1


def kelly_fraction(win_prob: float, decimal_odds: float) -> float:
    """
    Full Kelly Criterion: f* = (bp - q) / b
    where b = decimal_odds - 1, p = win_prob, q = 1 - p.
    Returns fraction of bankroll to wager. Capped at 0 (no bet if negative edge).
    """
    b = decimal_odds - 1
    if b <= 0:
        return 0.0
    q = 1 - win_prob
    f = (b * win_prob - q) / b
    return max(f, 0.0)


def suggested_units(kelly_frac: float, fractional: float = 0.25) -> float:
    """
    Convert Kelly fraction to unit recommendation.
    Uses fractional Kelly (default 25%) for safety.
    Maps to 0.5 - 3.0 unit scale.
    """
    adjusted = kelly_frac * fractional
    # Scale: 1% Kelly → 0.5u, 5% → 1.5u, 10%+ → 3u
    if adjusted <= 0:
        return 0
    units = min(adjusted * 30, 3.0)  # 30x multiplier, capped at 3 units
    return round(max(units, 0.5), 1)  # Floor at 0.5 if positive edge


class EdgeService:
    """Finds edges between engine confidence and market-implied probability."""

    def calculate_edge(
        self,
        engine_confidence: float,
        over_price: Optional[int],
        under_price: Optional[int],
        direction: str,
    ) -> dict:
        """
        Calculate the edge between our engine's confidence and the market.

        Returns dict with edge_pct, implied_prob, kelly_fraction, suggested_units.
        """
        # Convert engine confidence (0-100) to win probability (0-1)
        # Confidence 60 = 60% win rate for the suggested direction
        win_prob = engine_confidence / 100.0

        # Get implied probability from the book's price for our direction
        if direction.upper() == "OVER" and over_price is not None:
            implied = american_to_implied_prob(over_price)
            decimal = american_to_decimal(over_price)
        elif direction.upper() == "UNDER" and under_price is not None:
            implied = american_to_implied_prob(under_price)
            decimal = american_to_decimal(under_price)
        else:
            return {
                "edge_pct": 0,
                "implied_prob": None,
                "kelly_fraction": 0,
                "suggested_units": 0,
                "has_edge": False,
            }

        edge = win_prob - implied
        kelly = kelly_fraction(win_prob, decimal)
        units = suggested_units(kelly)

        return {
            "edge_pct": round(edge * 100, 1),
            "implied_prob": round(implied * 100, 1),
            "engine_prob": round(win_prob * 100, 1),
            "kelly_fraction": round(kelly, 4),
            "suggested_units": units,
            "has_edge": edge > 0.02,  # Require at least 2% edge
        }

    def find_edges(
        self,
        db: Session,
        week: int,
        min_edge: float = 2.0,
        min_confidence: float = 55.0,
        limit: int = 30,
    ) -> list[dict]:
        """
        Find the biggest edges across all projections for a week.
        Returns sorted list of edges (biggest first).
        """
        projections = db.query(PlayerProjection).filter(
            PlayerProjection.week == week,
            PlayerProjection.confidence >= min_confidence,
            PlayerProjection.confidence.isnot(None),
            PlayerProjection.direction.isnot(None),
        ).all()

        edges = []
        for proj in projections:
            player = db.query(Player).filter(Player.id == proj.player_id).first()
            if not player:
                continue

            # Get best odds for this player+stat
            best_odds = db.query(BookOdds).filter(
                BookOdds.player_id == proj.player_id,
                BookOdds.stat_type == proj.stat_type,
                BookOdds.week == week,
            ).all()

            if not best_odds:
                continue

            # Find best price for our direction
            direction = "OVER" if proj.confidence >= 50 else "UNDER"
            best_book = None
            best_price = None

            for odds in best_odds:
                if direction == "OVER" and odds.over_price is not None:
                    if best_price is None or odds.over_price > best_price:
                        best_price = odds.over_price
                        best_book = odds
                elif direction == "UNDER" and odds.under_price is not None:
                    if best_price is None or odds.under_price > best_price:
                        best_price = odds.under_price
                        best_book = odds

            if not best_book:
                continue

            edge_data = self.calculate_edge(
                proj.confidence,
                best_book.over_price,
                best_book.under_price,
                direction,
            )

            if edge_data["edge_pct"] < min_edge:
                continue

            edges.append({
                "player_id": player.id,
                "player_name": player.name,
                "team": player.team,
                "position": player.position,
                "headshot_url": player.headshot_url,
                "stat_type": proj.stat_type,
                "line": best_book.line,
                "direction": direction,
                "confidence": proj.confidence,
                "best_book": best_book.bookmaker,
                "best_price": best_price,
                "implied_line": proj.implied_line,
                "engine_projection": proj.engine_projection,
                **edge_data,
                "agent_breakdown": proj.agent_breakdown,
            })

        # Sort by edge descending
        edges.sort(key=lambda x: x["edge_pct"], reverse=True)
        return edges[:limit]

    def get_bet_sizing(
        self,
        confidence: float,
        american_odds: int,
        bankroll: float = 100.0,
    ) -> dict:
        """Calculate bet sizing recommendation for a specific bet."""
        win_prob = confidence / 100.0
        decimal = american_to_decimal(american_odds)
        kelly = kelly_fraction(win_prob, decimal)
        units = suggested_units(kelly)

        return {
            "full_kelly_pct": round(kelly * 100, 2),
            "quarter_kelly_pct": round(kelly * 25, 2),
            "suggested_units": units,
            "suggested_wager": round(bankroll * kelly * 0.25, 2),  # Quarter Kelly
            "potential_profit": round(bankroll * kelly * 0.25 * (decimal - 1), 2),
            "risk_level": "low" if units <= 1 else "medium" if units <= 2 else "high",
        }


edge_service = EdgeService()
