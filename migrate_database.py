"""
Database migration script to add auto-scoring columns to legs table.

Adds:
- actual_value (REAL): The actual stat value the player achieved
- scored_date (TEXT): ISO timestamp when the leg was scored
"""

import sqlite3
from pathlib import Path


def migrate_database(db_path: Path = None):
    """Add auto-scoring columns to legs table"""
    if db_path is None:
        db_path = Path(__file__).parent / "bets.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"\n[MIGRATION] Migrating database: {db_path}")

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(legs)")
    columns = [row[1] for row in cursor.fetchall()]

    migrations_needed = []

    if 'actual_value' not in columns:
        migrations_needed.append('actual_value')

    if 'scored_date' not in columns:
        migrations_needed.append('scored_date')

    if not migrations_needed:
        print("[OK] Database is already up to date!")
        conn.close()
        return

    print(f"\n[MIGRATION] Adding columns: {', '.join(migrations_needed)}")

    # Add columns if needed
    if 'actual_value' in migrations_needed:
        cursor.execute("ALTER TABLE legs ADD COLUMN actual_value REAL DEFAULT NULL")
        print("  [OK] Added: actual_value (REAL)")

    if 'scored_date' in migrations_needed:
        cursor.execute("ALTER TABLE legs ADD COLUMN scored_date TEXT DEFAULT NULL")
        print("  [OK] Added: scored_date (TEXT)")

    conn.commit()
    conn.close()

    print("\n[OK] Migration complete!\n")


if __name__ == "__main__":
    migrate_database()
