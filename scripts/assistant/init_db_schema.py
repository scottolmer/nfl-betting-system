"""
Database Schema Extension for Betting Assistant
Adds tables for Pick6 learning, constraint management, and conversation tracking
"""

import sqlite3
from datetime import datetime
from pathlib import Path


def extend_database_schema(db_path: str = "bets.db"):
    """Add new tables for betting assistant functionality"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table 1: Pick6 Availability Tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pick6_availability (
            player_name TEXT NOT NULL,
            prop_type TEXT NOT NULL,
            platform TEXT DEFAULT 'pick6',
            is_available INTEGER DEFAULT 1,
            confidence REAL DEFAULT 1.0,
            last_updated TEXT NOT NULL,
            source TEXT,
            notes TEXT,
            PRIMARY KEY (player_name, prop_type, platform)
        )
    """)

    # Table 2: Constraint Rules
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS constraint_rules (
            rule_id TEXT PRIMARY KEY,
            rule_type TEXT NOT NULL,
            rule_data TEXT NOT NULL,
            platform TEXT DEFAULT 'pick6',
            auto_apply INTEGER DEFAULT 1,
            created_date TEXT NOT NULL,
            times_applied INTEGER DEFAULT 0,
            last_applied TEXT
        )
    """)

    # Table 3: Conversation History
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_id TEXT DEFAULT 'default',
            timestamp TEXT NOT NULL,
            user_message TEXT,
            assistant_response TEXT,
            intent_detected TEXT,
            actions_taken TEXT
        )
    """)

    # Table 4: User Preferences
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            default_platform TEXT DEFAULT 'pick6',
            default_confidence_threshold INTEGER DEFAULT 65,
            preferred_prop_types TEXT,
            auto_apply_constraints INTEGER DEFAULT 1,
            created_date TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    """)

    # Create indexes for performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pick6_player
        ON pick6_availability(player_name)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversation_session
        ON conversation_history(session_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_conversation_timestamp
        ON conversation_history(timestamp)
    """)

    # Initialize default user preferences
    cursor.execute("""
        INSERT OR IGNORE INTO user_preferences
        (user_id, default_platform, default_confidence_threshold,
         preferred_prop_types, auto_apply_constraints, created_date, last_updated)
        VALUES
        ('default', 'pick6', 65, NULL, 1, ?, ?)
    """, (datetime.now().isoformat(), datetime.now().isoformat()))

    conn.commit()
    conn.close()

    print("[SUCCESS] Database schema extended successfully!")
    print("   Added tables:")
    print("   - pick6_availability")
    print("   - constraint_rules")
    print("   - conversation_history")
    print("   - user_preferences")


if __name__ == "__main__":
    extend_database_schema()
