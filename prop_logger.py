"""
Prop Logger - Save analyzed props to database for comprehensive scoring

Logs all analyzed props (not just bet-on parlays) to enable:
- Scoring every prediction for better calibration
- Identifying which prop types perform best
- Larger sample sizes for statistical significance
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


def log_analyzed_props(
    props_analyses: List,
    week: int,
    db_path: Path = None,
    top_n: int = None
) -> int:
    """
    Log analyzed props to database for later scoring.

    Args:
        props_analyses: List of PropAnalysis objects from PropAnalyzer
        week: NFL week number
        db_path: Path to database
        top_n: If set, only log top N props by confidence

    Returns:
        Number of props logged
    """
    if db_path is None:
        db_path = Path(__file__).parent / "bets.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Sort by confidence descending
    sorted_props = sorted(props_analyses, key=lambda x: x.final_confidence, reverse=True)

    # Limit to top N if specified
    if top_n:
        sorted_props = sorted_props[:top_n]

    logged_count = 0
    skipped_duplicates = 0

    for analysis in sorted_props:
        prop = analysis.prop

        # Create unique prop_id
        prop_id = f"prop_{week}_{prop.player_name}_{prop.stat_type}_{prop.bet_type}_{prop.line}".replace(" ", "_").lower()

        # Extract agent scores from agent_breakdown
        agent_scores = {}
        if hasattr(analysis, 'agent_breakdown') and analysis.agent_breakdown:
            for agent_name, breakdown in analysis.agent_breakdown.items():
                if isinstance(breakdown, dict) and 'raw_score' in breakdown:
                    agent_scores[agent_name] = breakdown['raw_score']

        try:
            cursor.execute("""
                INSERT INTO analyzed_props
                (prop_id, week, player, team, opponent, prop_type, bet_type, line,
                 confidence, agent_scores, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prop_id,
                week,
                prop.player_name,
                prop.team,
                prop.opponent,
                prop.stat_type,
                getattr(prop, 'bet_type', 'OVER'),
                prop.line,
                analysis.final_confidence,
                json.dumps(agent_scores),
                datetime.now().isoformat()
            ))
            logged_count += 1

        except sqlite3.IntegrityError:
            # Duplicate - already logged
            skipped_duplicates += 1
            continue

    conn.commit()
    conn.close()

    return logged_count, skipped_duplicates


def get_analyzed_props(week: int, db_path: Path = None) -> List[Dict]:
    """
    Get all analyzed props for a week that need scoring.

    Args:
        week: NFL week number
        db_path: Path to database

    Returns:
        List of prop dictionaries
    """
    if db_path is None:
        db_path = Path(__file__).parent / "bets.db"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT prop_id, week, player, team, opponent, prop_type, bet_type, line,
               confidence, agent_scores, result, actual_value
        FROM analyzed_props
        WHERE week = ?
        ORDER BY confidence DESC
    """, (week,))

    props = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return props


def update_prop_results(
    prop_id: str,
    result: int,
    actual_value: float,
    db_path: Path = None
) -> None:
    """
    Update a prop with scoring results.

    Args:
        prop_id: Prop identifier
        result: 1 (hit), 0 (miss), None (unable to score)
        actual_value: Actual stat value achieved
        db_path: Path to database
    """
    if db_path is None:
        db_path = Path(__file__).parent / "bets.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE analyzed_props
        SET result = ?, actual_value = ?, scored_date = ?
        WHERE prop_id = ?
    """, (result, actual_value, datetime.now().isoformat(), prop_id))

    conn.commit()
    conn.close()


def get_props_summary(week: int = None, db_path: Path = None) -> Dict:
    """
    Get summary statistics for analyzed props.

    Args:
        week: NFL week number (None for all weeks)
        db_path: Path to database

    Returns:
        Dictionary with summary stats
    """
    if db_path is None:
        db_path = Path(__file__).parent / "bets.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if week:
        query = "SELECT COUNT(*), SUM(CASE WHEN result = 1 THEN 1 ELSE 0 END), SUM(CASE WHEN result IS NOT NULL THEN 1 ELSE 0 END) FROM analyzed_props WHERE week = ?"
        cursor.execute(query, (week,))
    else:
        query = "SELECT COUNT(*), SUM(CASE WHEN result = 1 THEN 1 ELSE 0 END), SUM(CASE WHEN result IS NOT NULL THEN 1 ELSE 0 END) FROM analyzed_props"
        cursor.execute(query)

    total, hits, scored = cursor.fetchone()
    conn.close()

    return {
        'total': total or 0,
        'hits': hits or 0,
        'scored': scored or 0,
        'pending': (total or 0) - (scored or 0),
        'hit_rate': (hits / scored * 100) if scored else 0
    }
