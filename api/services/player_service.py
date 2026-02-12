"""Player service: roster sync, ESPN headshots, search."""

import logging
from typing import Optional
import httpx
from sqlalchemy.orm import Session
from api.database import Player, PlayerProjection

logger = logging.getLogger(__name__)

# ESPN public API endpoints
ESPN_TEAMS_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams"
ESPN_ROSTER_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/roster"

# NFL team abbreviation → ESPN team ID mapping
TEAM_ESPN_IDS = {
    "ARI": 22, "ATL": 1, "BAL": 33, "BUF": 2, "CAR": 29, "CHI": 3,
    "CIN": 4, "CLE": 5, "DAL": 6, "DEN": 7, "DET": 8, "GB": 9,
    "HOU": 34, "IND": 11, "JAC": 30, "KC": 12, "LV": 13, "LAC": 24,
    "LAR": 14, "MIA": 15, "MIN": 16, "NE": 17, "NO": 18, "NYG": 19,
    "NYJ": 20, "PHI": 21, "PIT": 23, "SF": 25, "SEA": 26, "TB": 27,
    "TEN": 10, "WAS": 28,
}


class PlayerService:
    """Manages player data, ESPN headshot syncing, and search."""

    def search(self, db: Session, query: str, position: Optional[str] = None, team: Optional[str] = None, limit: int = 20) -> list[Player]:
        """Search players by name with optional position/team filters."""
        q = db.query(Player).filter(Player.name.ilike(f"%{query}%"))
        if position:
            q = q.filter(Player.position == position.upper())
        if team:
            q = q.filter(Player.team == team.upper())
        return q.order_by(Player.name).limit(limit).all()

    def get_by_id(self, db: Session, player_id: int) -> Optional[Player]:
        return db.query(Player).filter(Player.id == player_id).first()

    def get_projections(self, db: Session, player_id: int, week: Optional[int] = None) -> list[PlayerProjection]:
        q = db.query(PlayerProjection).filter(PlayerProjection.player_id == player_id)
        if week:
            q = q.filter(PlayerProjection.week == week)
        return q.order_by(PlayerProjection.week.desc()).all()

    def find_or_create(self, db: Session, name: str, team: str, position: str) -> Player:
        """Find existing player or create a new one."""
        player = db.query(Player).filter(
            Player.name == name,
            Player.team == team,
        ).first()
        if not player:
            player = Player(name=name, team=team, position=position)
            db.add(player)
            db.commit()
            db.refresh(player)
        return player

    async def sync_team_roster(self, db: Session, team_abbr: str) -> int:
        """Fetch roster from ESPN and upsert into Player table. Returns count of players synced."""
        team_id = TEAM_ESPN_IDS.get(team_abbr.upper())
        if not team_id:
            logger.warning(f"Unknown team abbreviation: {team_abbr}")
            return 0

        url = ESPN_ROSTER_URL.format(team_id=team_id)
        count = 0

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.error(f"ESPN roster fetch failed for {team_abbr}: {e}")
                return 0

        # ESPN roster response has athletes grouped by position category
        for group in data.get("athletes", []):
            for athlete in group.get("items", []):
                espn_id = str(athlete.get("id", ""))
                name = athlete.get("displayName", athlete.get("fullName", ""))
                position = athlete.get("position", {}).get("abbreviation", "")
                headshot_url = athlete.get("headshot", {}).get("href", "")

                if not name or not position:
                    continue

                # Upsert: find by espn_id or name+team
                existing = db.query(Player).filter(Player.espn_id == espn_id).first()
                if not existing:
                    existing = db.query(Player).filter(
                        Player.name == name, Player.team == team_abbr.upper()
                    ).first()

                if existing:
                    existing.espn_id = espn_id
                    existing.headshot_url = headshot_url or existing.headshot_url
                    existing.position = position
                    existing.team = team_abbr.upper()
                else:
                    existing = Player(
                        name=name,
                        team=team_abbr.upper(),
                        position=position,
                        espn_id=espn_id,
                        headshot_url=headshot_url,
                    )
                    db.add(existing)
                count += 1

        db.commit()
        logger.info(f"Synced {count} players for {team_abbr}")
        return count

    async def sync_all_rosters(self, db: Session) -> dict:
        """Sync rosters for all 32 NFL teams."""
        results = {}
        for team_abbr in TEAM_ESPN_IDS:
            results[team_abbr] = await self.sync_team_roster(db, team_abbr)
        return results


player_service = PlayerService()
