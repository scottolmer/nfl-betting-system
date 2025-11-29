"""
Database migration to add analyzed_props table for comprehensive prop scoring.

This table stores ALL analyzed props (not just parlays) so we can:
- Score every prediction, not just bet-on parlays
- Get better calibration data with larger sample sizes
- Identify which prop types the system excels at
"""

import sqlite3
from pathlib import Path


def migrate_database(db_path: Path = None):
    """Add analyzed_props table for comprehensive prop tracking"""
    if db_path is None:
        db_path = Path(__file__).parent / "bets.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"\n[MIGRATION] Adding analyzed_props table to: {db_path}")

    # Check if table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analyzed_props'")
    if cursor.fetchone():
        print("[OK] analyzed_props table already exists!")
        conn.close()
        return

    # Create analyzed_props table
    cursor.execute("""
        CREATE TABLE analyzed_props (
            prop_id TEXT PRIMARY KEY,
            week INTEGER,
            player TEXT,
            team TEXT,
            opponent TEXT,
            prop_type TEXT,
            bet_type TEXT,
            line REAL,
            confidence REAL,
            agent_scores TEXT,
            result INTEGER DEFAULT NULL,
            actual_value REAL DEFAULT NULL,
            scored_date TEXT DEFAULT NULL,
            created_date TEXT,
            UNIQUE(week, player, prop_type, bet_type, line)
        )
    """)

    # Create indexes for faster queries
    cursor.execute("CREATE INDEX idx_analyzed_props_week ON analyzed_props(week)")
    cursor.execute("CREATE INDEX idx_analyzed_props_player ON analyzed_props(player)")
    cursor.execute("CREATE INDEX idx_analyzed_props_confidence ON analyzed_props(confidence)")

    conn.commit()
    conn.close()

    print("  [OK] Created: analyzed_props table")
    print("  [OK] Created: indexes for week, player, confidence")
    print("\n[OK] Migration complete!\n")


if __name__ == "__main__":
    migrate_database()
