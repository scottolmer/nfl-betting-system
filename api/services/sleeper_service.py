"""
Sleeper API Service — Free, no-auth client for fantasy league data.

Sleeper API docs: https://docs.sleeper.com/
All endpoints are public and rate-limit friendly.
"""

import logging
import httpx
from typing import Optional
from sqlalchemy.orm import Session
from api.database import Player

logger = logging.getLogger(__name__)

SLEEPER_BASE = "https://api.sleeper.app/v1"

# Cache for the massive players endpoint (50k+ entries)
_players_cache: Optional[dict] = None


class SleeperService:
    """Client for Sleeper API with player ID mapping to our Player table."""

    async def get_user(self, username: str) -> Optional[dict]:
        """Fetch Sleeper user by username."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{SLEEPER_BASE}/user/{username}")
            if resp.status_code == 200 and resp.json():
                return resp.json()
            return None

    async def get_leagues(self, user_id: str, season: int = 2025) -> list[dict]:
        """Get all NFL leagues for a Sleeper user in a season."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{SLEEPER_BASE}/user/{user_id}/leagues/nfl/{season}")
            if resp.status_code == 200:
                return resp.json() or []
            return []

    async def get_league(self, league_id: str) -> Optional[dict]:
        """Get league details."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{SLEEPER_BASE}/league/{league_id}")
            if resp.status_code == 200:
                return resp.json()
            return None

    async def get_league_users(self, league_id: str) -> list[dict]:
        """Get all users in a league."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{SLEEPER_BASE}/league/{league_id}/users")
            if resp.status_code == 200:
                return resp.json() or []
            return []

    async def get_rosters(self, league_id: str) -> list[dict]:
        """Get all rosters in a league."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{SLEEPER_BASE}/league/{league_id}/rosters")
            if resp.status_code == 200:
                return resp.json() or []
            return []

    async def get_matchups(self, league_id: str, week: int) -> list[dict]:
        """Get matchups for a specific week."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{SLEEPER_BASE}/league/{league_id}/matchups/{week}")
            if resp.status_code == 200:
                return resp.json() or []
            return []

    async def get_nfl_state(self) -> Optional[dict]:
        """Get current NFL state (week, season, etc.)."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{SLEEPER_BASE}/state/nfl")
            if resp.status_code == 200:
                return resp.json()
            return None

    async def get_all_players(self) -> dict:
        """
        Get all NFL players from Sleeper (cached — this is a large payload).
        Returns dict keyed by Sleeper player_id.
        """
        global _players_cache
        if _players_cache is not None:
            return _players_cache

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{SLEEPER_BASE}/players/nfl")
            if resp.status_code == 200:
                _players_cache = resp.json()
                return _players_cache
        return {}

    def map_sleeper_player_to_db(
        self, db: Session, sleeper_id: str, sleeper_players: dict
    ) -> Optional[Player]:
        """
        Map a Sleeper player ID to our Player table.
        Uses name + team matching since Sleeper IDs don't map to ESPN IDs.
        """
        sp = sleeper_players.get(sleeper_id)
        if not sp or not sp.get("full_name"):
            return None

        name = sp["full_name"]
        team = sp.get("team") or ""

        # Try exact name + team match first
        player = db.query(Player).filter(
            Player.name == name,
            Player.team == team,
        ).first()

        if player:
            return player

        # Fallback: name-only match (team might differ between sources)
        player = db.query(Player).filter(Player.name == name).first()
        if player:
            return player

        # Create a new player record if we don't have them
        if team and sp.get("position"):
            player = Player(
                name=name,
                team=team,
                position=sp.get("position", ""),
                status="active" if sp.get("status") == "Active" else "inactive",
            )
            db.add(player)
            db.flush()
            return player

        return None

    async def get_user_roster(
        self, league_id: str, user_id: str
    ) -> Optional[dict]:
        """Find a specific user's roster in a league."""
        league_users = await self.get_league_users(league_id)
        rosters = await self.get_rosters(league_id)

        # Find roster_id owned by this user
        user_roster = None
        for roster in rosters:
            if roster.get("owner_id") == user_id:
                user_roster = roster
                break

        return user_roster

    async def get_matchup_opponent(
        self, league_id: str, week: int, roster_id: int
    ) -> Optional[dict]:
        """Find the opponent roster for a given week matchup."""
        matchups = await self.get_matchups(league_id, week)

        # Find user's matchup_id
        user_matchup = None
        for m in matchups:
            if m.get("roster_id") == roster_id:
                user_matchup = m
                break

        if not user_matchup:
            return None

        matchup_id = user_matchup.get("matchup_id")

        # Find opponent with same matchup_id
        for m in matchups:
            if m.get("matchup_id") == matchup_id and m.get("roster_id") != roster_id:
                return m

        return None


sleeper_service = SleeperService()
