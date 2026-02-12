"""Odds service: fetch from The Odds API, store BookOdds, find best prices, track line movement."""

import logging
from datetime import datetime, timezone
from typing import Optional
import httpx
from sqlalchemy.orm import Session
from api.config import settings
from api.database import BookOdds, LineMovement, Player

logger = logging.getLogger(__name__)

ODDS_API_BASE = "https://api.the-odds-api.com/v4"

# Map The Odds API stat keys to our internal stat types
STAT_TYPE_MAP = {
    "player_pass_yds": "pass_yds",
    "player_pass_tds": "pass_tds",
    "player_pass_completions": "pass_completions",
    "player_pass_attempts": "pass_attempts",
    "player_pass_interceptions": "pass_interceptions",
    "player_rush_yds": "rush_yds",
    "player_rush_attempts": "rush_attempts",
    "player_reception_yds": "rec_yds",
    "player_receptions": "receptions",
    "player_reception_tds": "rec_tds",
    "player_anytime_td": "anytime_td",
    "player_rush_reception_yds": "rush_rec_yds",
    "player_rush_reception_tds": "rush_rec_tds",
}

# Available player prop markets on The Odds API
PLAYER_PROP_MARKETS = [
    "player_pass_yds",
    "player_pass_tds",
    "player_pass_completions",
    "player_rush_yds",
    "player_reception_yds",
    "player_receptions",
    "player_anytime_td",
    "player_rush_reception_yds",
]


class OddsService:
    """Fetches odds from The Odds API and manages BookOdds/LineMovement storage."""

    def _get_api_key(self) -> str:
        key = settings.odds_api_key
        if not key:
            raise ValueError("ODDS_API_KEY not set in environment")
        return key

    async def fetch_player_props(self, db: Session, event_id: str, market: str) -> int:
        """Fetch player prop odds for a specific game and market. Returns count stored."""
        api_key = self._get_api_key()
        url = f"{ODDS_API_BASE}/sports/americanfootball_nfl/events/{event_id}/odds"
        params = {
            "apiKey": api_key,
            "regions": "us",
            "markets": market,
            "oddsFormat": "american",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.error(f"Odds API fetch failed for {event_id}/{market}: {e}")
                return 0

        return self._store_odds_from_response(db, data, market)

    async def fetch_upcoming_events(self) -> list[dict]:
        """Get list of upcoming NFL games from The Odds API."""
        api_key = self._get_api_key()
        url = f"{ODDS_API_BASE}/sports/americanfootball_nfl/events"
        params = {"apiKey": api_key}

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    async def fetch_all_props_for_week(self, db: Session, week: int) -> dict:
        """Fetch all player props for upcoming games. Returns summary of what was fetched."""
        events = await self.fetch_upcoming_events()
        summary = {"events": len(events), "total_odds": 0}

        for event in events:
            event_id = event.get("id")
            for market in PLAYER_PROP_MARKETS:
                count = await self.fetch_player_props(db, event_id, market)
                summary["total_odds"] += count

        return summary

    def _store_odds_from_response(self, db: Session, data: dict, market: str) -> int:
        """Parse The Odds API response and store odds. Returns count stored."""
        count = 0
        stat_type = STAT_TYPE_MAP.get(market, market)

        for bookmaker in data.get("bookmakers", []):
            book_key = bookmaker.get("key", "")
            for mkt in bookmaker.get("markets", []):
                outcomes = mkt.get("outcomes", [])
                # Group outcomes by player (Over/Under pairs)
                player_odds: dict[str, dict] = {}
                for outcome in outcomes:
                    player_name = outcome.get("description", "")
                    if not player_name:
                        continue
                    if player_name not in player_odds:
                        player_odds[player_name] = {}

                    side = outcome.get("name", "").lower()  # "Over" or "Under"
                    player_odds[player_name][side] = {
                        "price": outcome.get("price"),
                        "point": outcome.get("point"),
                    }

                for player_name, sides in player_odds.items():
                    over = sides.get("over", {})
                    under = sides.get("under", {})
                    line = over.get("point") or under.get("point")
                    if line is None:
                        continue

                    # Find or match player
                    player = db.query(Player).filter(
                        Player.name.ilike(f"%{player_name}%")
                    ).first()
                    player_id = player.id if player else None

                    if player_id is None:
                        # Create a minimal player record
                        new_player = Player(name=player_name, team="UNK", position="UNK")
                        db.add(new_player)
                        db.flush()
                        player_id = new_player.id

                    # Store current odds
                    odds_entry = BookOdds(
                        player_id=player_id,
                        week=0,  # Will be set by caller or pipeline
                        stat_type=stat_type,
                        bookmaker=book_key,
                        line=float(line),
                        over_price=over.get("price"),
                        under_price=under.get("price"),
                    )
                    db.add(odds_entry)

                    # Record line movement
                    movement = LineMovement(
                        player_id=player_id,
                        week=0,
                        stat_type=stat_type,
                        bookmaker=book_key,
                        line=float(line),
                        over_price=over.get("price"),
                        under_price=under.get("price"),
                    )
                    db.add(movement)
                    count += 1

        db.commit()
        return count

    def get_player_odds(self, db: Session, player_id: int, week: Optional[int] = None) -> list[BookOdds]:
        """Get all odds for a player, optionally filtered by week."""
        q = db.query(BookOdds).filter(BookOdds.player_id == player_id)
        if week:
            q = q.filter(BookOdds.week == week)
        return q.order_by(BookOdds.fetched_at.desc()).all()

    def get_best_prices(self, db: Session, player_id: int, stat_type: str, week: int) -> dict:
        """Find the best over and under prices across all books for a player prop."""
        odds = db.query(BookOdds).filter(
            BookOdds.player_id == player_id,
            BookOdds.stat_type == stat_type,
            BookOdds.week == week,
        ).all()

        if not odds:
            return {"player_id": player_id, "stat_type": stat_type, "best_over": None, "best_under": None}

        best_over = max(
            (o for o in odds if o.over_price is not None),
            key=lambda o: o.over_price,
            default=None,
        )
        best_under = max(
            (o for o in odds if o.under_price is not None),
            key=lambda o: o.under_price,
            default=None,
        )

        return {
            "player_id": player_id,
            "stat_type": stat_type,
            "best_over": {
                "bookmaker": best_over.bookmaker,
                "line": best_over.line,
                "price": best_over.over_price,
            } if best_over else None,
            "best_under": {
                "bookmaker": best_under.bookmaker,
                "line": best_under.line,
                "price": best_under.under_price,
            } if best_under else None,
        }

    def get_line_movement(self, db: Session, player_id: int, stat_type: str, week: int) -> list[dict]:
        """Get line movement history for a player prop."""
        movements = db.query(LineMovement).filter(
            LineMovement.player_id == player_id,
            LineMovement.stat_type == stat_type,
            LineMovement.week == week,
        ).order_by(LineMovement.recorded_at.asc()).all()

        return [
            {
                "bookmaker": m.bookmaker,
                "line": m.line,
                "over_price": m.over_price,
                "under_price": m.under_price,
                "recorded_at": m.recorded_at.isoformat() if m.recorded_at else None,
            }
            for m in movements
        ]


odds_service = OddsService()
