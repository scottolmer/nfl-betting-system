"""
Projection Service — Single source of truth for all three pillars.

Key insight: Use betting lines as the baseline projection model,
then let the agent engine find where lines are wrong.
That single analysis feeds DFS, Props, and Fantasy modes.
"""

import logging
import math
from typing import Optional
from sqlalchemy.orm import Session
from api.database import Player, PlayerProjection, BookOdds
from api.services.odds_service import odds_service
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.data_loader import NFLDataLoader

logger = logging.getLogger(__name__)


def american_to_implied_prob(american_odds: int) -> float:
    """Convert American odds to implied probability."""
    if american_odds > 0:
        return 100.0 / (american_odds + 100)
    else:
        return abs(american_odds) / (abs(american_odds) + 100)


def implied_line_from_odds(over_price: Optional[int], under_price: Optional[int], line: float) -> float:
    """
    Derive the 'true' implied projection from over/under pricing.

    If over is juiced (e.g. -130), the market expects the over to hit more often,
    meaning the true mean is above the posted line. We shift accordingly.
    """
    if over_price is None or under_price is None:
        return line  # No pricing data, use line as-is

    over_prob = american_to_implied_prob(over_price)
    under_prob = american_to_implied_prob(under_price)

    # Remove vig: normalize to sum to 1.0
    total = over_prob + under_prob
    if total == 0:
        return line
    over_fair = over_prob / total
    under_fair = under_prob / total

    # Shift line based on fair probability skew
    # If over_fair > 0.5, market expects stat to exceed line
    # Magnitude: a 55/45 split shifts ~5% of the line
    skew = over_fair - 0.5  # positive = market expects over
    shift_pct = skew * 0.10  # 10% of line per 50% skew (conservative)
    implied = line * (1 + shift_pct)

    return round(implied, 1)


class ProjectionService:
    """
    Generates projections by combining odds-implied baselines with agent analysis.

    Flow:
    1. Gather BookOdds across all books for a player+stat+week
    2. Derive consensus line and implied projection from pricing
    3. Run agent engine to find edges vs the line
    4. Store final projection with confidence and agent breakdown
    """

    def __init__(self, data_dir: str = "data"):
        self.analyzer = PropAnalyzer(use_dynamic_weights=True)
        self.loader = NFLDataLoader(data_dir=data_dir)

    def get_consensus_line(self, db: Session, player_id: int, stat_type: str, week: int) -> Optional[dict]:
        """
        Calculate consensus line from all bookmakers.
        Returns dict with consensus_line, implied_projection, book_count, lines.
        """
        odds = db.query(BookOdds).filter(
            BookOdds.player_id == player_id,
            BookOdds.stat_type == stat_type,
            BookOdds.week == week,
        ).all()

        if not odds:
            return None

        lines = [o.line for o in odds]
        consensus_line = round(sum(lines) / len(lines), 1)

        # Calculate implied projection from best-priced book
        implied_projections = []
        for o in odds:
            implied = implied_line_from_odds(o.over_price, o.under_price, o.line)
            implied_projections.append(implied)

        avg_implied = round(sum(implied_projections) / len(implied_projections), 1)

        return {
            "consensus_line": consensus_line,
            "implied_projection": avg_implied,
            "book_count": len(odds),
            "lines": {o.bookmaker: {"line": o.line, "over": o.over_price, "under": o.under_price} for o in odds},
        }

    def generate_projection(
        self,
        db: Session,
        player_id: int,
        stat_type: str,
        week: int,
        context: Optional[dict] = None,
    ) -> Optional[PlayerProjection]:
        """
        Generate a projection for a single player+stat+week.

        1. Get consensus line from BookOdds
        2. Run agent analysis against that line
        3. Combine into final engine projection
        4. Store in PlayerProjection table
        """
        player = db.query(Player).filter(Player.id == player_id).first()
        if not player:
            return None

        # Step 1: Consensus line
        consensus = self.get_consensus_line(db, player_id, stat_type, week)
        implied_line = consensus["implied_projection"] if consensus else None
        base_line = consensus["consensus_line"] if consensus else None

        # Step 2: Load analysis context if not provided
        if context is None:
            context = self.loader.load_all_data(week=week)

        # Step 3: Run agent analysis against the line
        confidence = None
        direction = None
        agent_breakdown = {}

        if base_line is not None:
            # Build a prop dict matching what PropAnalyzer expects
            prop_data = {
                "player": player.name,
                "team": player.team,
                "position": player.position,
                "opponent": "",  # Will be resolved by analyzer
                "stat_type": stat_type,
                "line": base_line,
                "bet_type": "OVER",  # Analyze from over perspective; confidence < 50 means under
            }

            try:
                analysis = self.analyzer.analyze_prop(prop_data, context)
                if analysis:
                    confidence = analysis.final_confidence
                    direction = analysis.recommendation
                    agent_breakdown = {
                        agent_name: {
                            "score": result.get("raw_score"),
                            "weight": result.get("weight"),
                            "direction": result.get("direction"),
                        }
                        for agent_name, result in analysis.agent_breakdown.items()
                    }
            except Exception as e:
                logger.warning(f"Agent analysis failed for {player.name} {stat_type}: {e}")

        # Step 4: Calculate engine projection
        # Start from implied line, adjust based on agent confidence
        engine_projection = implied_line
        if engine_projection and confidence is not None:
            # If confidence > 60 for OVER, nudge projection up
            # If confidence < 40 (i.e. UNDER signal), nudge down
            edge_magnitude = (confidence - 50) / 50  # -1 to +1
            adjust_pct = edge_magnitude * 0.05  # Max 5% adjustment
            engine_projection = round(engine_projection * (1 + adjust_pct), 1)

        # Step 5: Upsert projection
        existing = db.query(PlayerProjection).filter(
            PlayerProjection.player_id == player_id,
            PlayerProjection.week == week,
            PlayerProjection.stat_type == stat_type,
        ).first()

        if existing:
            existing.implied_line = implied_line
            existing.engine_projection = engine_projection
            existing.confidence = confidence
            existing.direction = direction
            existing.agent_breakdown = agent_breakdown
            projection = existing
        else:
            projection = PlayerProjection(
                player_id=player_id,
                week=week,
                stat_type=stat_type,
                implied_line=implied_line,
                engine_projection=engine_projection,
                confidence=confidence,
                direction=direction,
                agent_breakdown=agent_breakdown,
            )
            db.add(projection)

        db.commit()
        db.refresh(projection)
        return projection

    def generate_all_projections_for_week(self, db: Session, week: int) -> list[PlayerProjection]:
        """Generate projections for all players with odds data for a given week."""
        # Load context once for the whole week
        context = self.loader.load_all_data(week=week)

        # Find all distinct player+stat combos with odds this week
        odds_combos = db.query(
            BookOdds.player_id, BookOdds.stat_type
        ).filter(
            BookOdds.week == week
        ).distinct().all()

        projections = []
        for player_id, stat_type in odds_combos:
            proj = self.generate_projection(db, player_id, stat_type, week, context=context)
            if proj:
                projections.append(proj)

        logger.info(f"Generated {len(projections)} projections for week {week}")
        return projections

    def get_top_edges(self, db: Session, week: int, limit: int = 20) -> list[dict]:
        """Get projections with the biggest edges (highest confidence divergence from line)."""
        projections = db.query(PlayerProjection).filter(
            PlayerProjection.week == week,
            PlayerProjection.confidence.isnot(None),
        ).order_by(PlayerProjection.confidence.desc()).limit(limit).all()

        results = []
        for p in projections:
            player = db.query(Player).filter(Player.id == p.player_id).first()
            results.append({
                "player_id": p.player_id,
                "player_name": player.name if player else "Unknown",
                "team": player.team if player else "",
                "position": player.position if player else "",
                "stat_type": p.stat_type,
                "implied_line": p.implied_line,
                "engine_projection": p.engine_projection,
                "confidence": p.confidence,
                "direction": p.direction,
                "agent_breakdown": p.agent_breakdown,
            })

        return results


projection_service = ProjectionService()
