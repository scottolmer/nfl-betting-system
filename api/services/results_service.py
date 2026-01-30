"""
Results Service - Business logic for parlay scoring and results

Wraps auto_scorer.py functionality for API consumption
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import sqlite3
from datetime import datetime

# Add parent directory to path to import auto_scorer
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import auto_scorer


class ResultsService:
    """Service for parlay scoring and results retrieval"""

    def __init__(self, db_path: Path = None, data_dir: Path = None):
        """
        Initialize results service

        Args:
            db_path: Path to SQLite database (default: bets.db in project root)
            data_dir: Path to data directory (default: data/ in project root)
        """
        if db_path is None:
            self.db_path = Path(__file__).parent.parent.parent / "bets.db"
        else:
            self.db_path = Path(db_path)

        if data_dir is None:
            self.data_dir = Path(__file__).parent.parent.parent / "data"
        else:
            self.data_dir = Path(data_dir)

    def score_week(
        self,
        week: int,
        dry_run: bool = False,
        force: bool = False
    ) -> Dict:
        """
        Score all parlays for a specific week

        Args:
            week: NFL week number (1-18)
            dry_run: If True, don't commit to database
            force: If True, re-score already scored parlays

        Returns:
            {
                "week": 17,
                "parlays_scored": 5,
                "wins": 3,
                "losses": 2,
                "pending": 0,
                "results": [...]
            }
        """
        # Load week stats
        week_stats = auto_scorer.load_week_stats(week, self.data_dir)

        if not week_stats:
            return {
                "success": False,
                "error": f"No CSV files found for Week {week}",
                "week": week
            }

        # Get parlays to score
        parlays = auto_scorer.get_pending_parlays(week, self.db_path, include_scored=force)

        if not parlays:
            return {
                "success": True,
                "week": week,
                "parlays_scored": 0,
                "wins": 0,
                "losses": 0,
                "pending": 0,
                "message": f"No {'parlays' if force else 'pending parlays'} found for Week {week}",
                "results": []
            }

        # Score each parlay
        results = []
        wins = 0
        losses = 0
        pending = 0

        for parlay in parlays:
            result = auto_scorer.score_parlay(parlay, week_stats)

            # Update database (unless dry run)
            if not dry_run:
                leg_results = [
                    {
                        'leg_id': leg['leg_id'],
                        'result': leg['result'],
                        'actual_value': leg['actual_value']
                    }
                    for leg in result['scored_legs']
                ]
                auto_scorer.update_parlay_results(
                    result['parlay_id'],
                    leg_results,
                    self.db_path,
                    dry_run=False
                )

            # Count results
            if result['overall_result'] == 'WIN':
                wins += 1
            elif result['overall_result'] == 'LOSS':
                losses += 1
            else:
                pending += 1

            results.append(result)

        return {
            "success": True,
            "week": week,
            "parlays_scored": len(results),
            "wins": wins,
            "losses": losses,
            "pending": pending,
            "dry_run": dry_run,
            "results": results
        }

    def get_parlay_results_for_week(self, week: int) -> Dict:
        """
        Get all graded parlays for a specific week

        Args:
            week: NFL week number

        Returns:
            {
                "week": 17,
                "parlays": [...]
            }
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dicts
        cursor = conn.cursor()

        # Query parlays for this week
        parlay_rows = cursor.execute(
            """
            SELECT parlay_id, week, confidence_score, status
            FROM parlays
            WHERE week = ?
            ORDER BY confidence_score DESC
            """,
            (week,)
        ).fetchall()

        parlays = []
        for parlay_row in parlay_rows:
            parlay_id = parlay_row['parlay_id']

            # Get legs for this parlay
            leg_rows = cursor.execute(
                """
                SELECT leg_id, player, team, prop_type, bet_type, line, result, actual_value
                FROM legs
                WHERE parlay_id = ?
                """,
                (parlay_id,)
            ).fetchall()

            legs = []
            legs_hit = 0
            legs_total = len(leg_rows)

            for leg_row in leg_rows:
                leg_data = {
                    "leg_id": leg_row['leg_id'],
                    "player": leg_row['player'],
                    "team": leg_row['team'],
                    "prop_type": leg_row['prop_type'],
                    "bet_type": leg_row['bet_type'],
                    "line": leg_row['line'],
                    "result": leg_row['result'],
                    "actual_value": leg_row['actual_value']
                }
                legs.append(leg_data)

                if leg_row['result'] == 1:
                    legs_hit += 1

            parlay_data = {
                "parlay_id": parlay_id,
                "week": parlay_row['week'],
                "confidence_score": parlay_row['confidence_score'],
                "status": parlay_row['status'],
                "legs_hit": legs_hit,
                "legs_total": legs_total,
                "legs": legs
            }

            parlays.append(parlay_data)

        conn.close()

        return {
            "success": True,
            "week": week,
            "parlay_count": len(parlays),
            "parlays": parlays
        }

    def get_parlay_result(self, parlay_id: str) -> Optional[Dict]:
        """
        Get result for a specific parlay

        Args:
            parlay_id: Parlay ID

        Returns:
            Parlay data with legs and results, or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Query parlay
        parlay_row = cursor.execute(
            """
            SELECT parlay_id, week, confidence_score, status
            FROM parlays
            WHERE parlay_id = ?
            """,
            (parlay_id,)
        ).fetchone()

        if not parlay_row:
            conn.close()
            return None

        # Get legs
        leg_rows = cursor.execute(
            """
            SELECT leg_id, player, team, prop_type, bet_type, line, result, actual_value, scored_date
            FROM legs
            WHERE parlay_id = ?
            """,
            (parlay_id,)
        ).fetchall()

        legs = []
        legs_hit = 0
        legs_total = len(leg_rows)

        for leg_row in leg_rows:
            leg_data = {
                "leg_id": leg_row['leg_id'],
                "player": leg_row['player'],
                "team": leg_row['team'],
                "prop_type": leg_row['prop_type'],
                "bet_type": leg_row['bet_type'],
                "line": leg_row['line'],
                "result": leg_row['result'],
                "actual_value": leg_row['actual_value'],
                "scored_date": leg_row['scored_date']
            }
            legs.append(leg_data)

            if leg_row['result'] == 1:
                legs_hit += 1

        conn.close()

        return {
            "success": True,
            "parlay_id": parlay_id,
            "week": parlay_row['week'],
            "confidence_score": parlay_row['confidence_score'],
            "status": parlay_row['status'],
            "legs_hit": legs_hit,
            "legs_total": legs_total,
            "legs": legs
        }

    def sync_parlay_from_mobile(self, parlay_data: Dict) -> Dict:
        """
        Sync a parlay from mobile app to backend database

        Args:
            parlay_data: Parlay data from mobile app (SavedParlay format)

        Returns:
            {
                "success": True,
                "parlay_id": "uuid",
                "synced": True
            }
        """
        import uuid

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Generate parlay ID if not provided
        parlay_id = parlay_data.get('backend_id') or parlay_data.get('id') or str(uuid.uuid4())

        # Check if parlay already exists
        existing = cursor.execute(
            "SELECT parlay_id FROM parlays WHERE parlay_id = ?",
            (parlay_id,)
        ).fetchone()

        if existing:
            conn.close()
            return {
                "success": True,
                "parlay_id": parlay_id,
                "synced": True,
                "message": "Parlay already synced"
            }

        # Insert parlay
        cursor.execute(
            """
            INSERT INTO parlays (parlay_id, week, confidence_score, status)
            VALUES (?, ?, ?, 'pending')
            """,
            (parlay_id, parlay_data['week'], parlay_data['combined_confidence'])
        )

        # Insert legs
        for leg in parlay_data['legs']:
            leg_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO legs (leg_id, parlay_id, player, team, prop_type, bet_type, line)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    leg_id,
                    parlay_id,
                    leg['player_name'],
                    leg['team'],
                    leg['stat_type'],
                    leg['bet_type'],
                    leg['line']
                )
            )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "parlay_id": parlay_id,
            "synced": True,
            "legs_synced": len(parlay_data['legs'])
        }


# Export singleton instance
results_service = ResultsService()
