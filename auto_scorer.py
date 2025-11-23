"""
Auto-Scoring System for NFL Betting Parlays

Automatically scores parlays by comparing predicted props against actual player
performance from weekly CSV files.

Usage:
    python auto_scorer.py --week 10 --dry-run
    python auto_scorer.py --week 10
    python auto_scorer.py --week 10 --force
"""

import sqlite3
import pandas as pd
from pathlib import Path
import re
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys


# ============================================================================
# CONFIGURATION
# ============================================================================

# Map prop types to CSV sources and column names
STAT_TYPE_MAP = {
    # Passing stats
    "Pass Yds": [("passing", "YDS")],
    "Pass TDs": [("passing", "TD")],
    "Pass Completions": [("passing", "COM")],
    "Pass Attempts": [("passing", "ATT")],

    # Rushing stats
    "Rush Yds": [("rushing", "YDS")],
    "Rush TDs": [("rushing", "TD")],
    "Rush Attempts": [("rushing", "ATT")],

    # Receiving stats
    "Rec Yds": [("receiving", "YDS")],
    "Rec TDs": [("receiving", "TD")],
    "Receptions": [("receiving", "REC")],

    # Combined stats (sum multiple sources)
    "Rush+Rec Yds": [
        ("rushing", "YDS"),
        ("receiving", "YDS")
    ],

    # Potential future combined stats
    "Pass+Rush Yds": [
        ("passing", "YDS"),
        ("rushing", "YDS")
    ],
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def normalize_name(name: str) -> str:
    """Normalize player name for matching (same as data_loader.py)"""
    if not name:
        return name
    name = str(name).strip().replace('.', '')
    name = re.sub(r'\s+', ' ', name)
    return name.lower()


def normalize_team_abbr(abbr: str) -> str:
    """Normalize team abbreviations to handle variations"""
    if not abbr:
        return abbr
    abbr = str(abbr).strip().upper()
    team_map = {
        'JAX': 'JAC',
        'ARZ': 'ARI',
        'BLT': 'BAL',
        'CLV': 'CLE',
        'HST': 'HOU',
    }
    return team_map.get(abbr, abbr)


def load_csv_with_conflict_handling(file_path: Path) -> pd.DataFrame:
    """
    Load CSV file, skipping git merge conflict markers.

    Handles files with:
    <<<<<<< HEAD
    [data]
    =======
    [duplicate data]
    >>>>>>> commit_hash
    """
    if not file_path.exists():
        return None

    lines = []
    in_conflict = False
    found_separator = False

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_stripped = line.strip()

            # Skip conflict markers
            if line_stripped.startswith('<<<<<<<'):
                in_conflict = True
                continue
            elif line_stripped.startswith('======='):
                found_separator = True
                continue
            elif line_stripped.startswith('>>>>>>>'):
                in_conflict = False
                found_separator = False
                continue

            # If we've seen the separator, skip duplicate data
            if found_separator:
                continue

            # Keep valid lines
            if line_stripped:
                lines.append(line)

    if not lines:
        return None

    # Parse CSV from cleaned lines
    from io import StringIO
    csv_content = ''.join(lines)

    try:
        # Read CSV, skip the first row (category headers like "BASIC,BASIC,USAGE...")
        df = pd.read_csv(StringIO(csv_content), skiprows=1)
        return df
    except Exception as e:
        print(f"[WARNING] Error parsing {file_path.name}: {e}")
        return None


# ============================================================================
# CSV DATA LOADING
# ============================================================================

def load_week_stats(week: int, data_dir: Path = None) -> Dict[str, pd.DataFrame]:
    """
    Load all stat CSVs for a given week.

    Returns:
        {
            'passing': DataFrame,
            'rushing': DataFrame,
            'receiving': DataFrame
        }
    """
    if data_dir is None:
        data_dir = Path(__file__).parent / "data"

    week_stats = {}
    stat_types = ['passing', 'rushing', 'receiving']

    print(f"\n[LOADING] Loading Week {week} CSV files...")

    for stat_type in stat_types:
        file_name = f"wk{week}_{stat_type}_base.csv"
        file_path = data_dir / file_name

        df = load_csv_with_conflict_handling(file_path)

        if df is not None:
            # Normalize player names for matching
            if 'Player' in df.columns:
                df['Player_Normalized'] = df['Player'].apply(normalize_name)

            # Normalize team abbreviations
            if 'Tm' in df.columns:
                df['Tm'] = df['Tm'].apply(normalize_team_abbr)

            week_stats[stat_type] = df
            print(f"  [OK] Loaded {file_name}: {len(df)} players")
        else:
            print(f"  [WARNING] Could not load {file_name}")

    return week_stats


def find_player_stat(
    player_name: str,
    stat_config: List[Tuple[str, str]],
    week_stats: Dict[str, pd.DataFrame]
) -> Tuple[Optional[float], List[str]]:
    """
    Find a player's stat value, handling single and combined stats.

    Args:
        player_name: Player name (will be normalized)
        stat_config: List of (csv_type, column_name) tuples
                    e.g., [("passing", "YDS")] or [("rushing", "YDS"), ("receiving", "YDS")]
        week_stats: Dictionary of loaded DataFrames

    Returns:
        (stat_value, debug_info)
        - stat_value: Total stat value, or None if player not found
        - debug_info: List of strings describing what was found
    """
    player_normalized = normalize_name(player_name)
    total = 0.0
    debug_info = []
    found_any = False

    for csv_type, column in stat_config:
        df = week_stats.get(csv_type)

        if df is None:
            debug_info.append(f"  ⚠️  {csv_type}.csv not loaded")
            continue

        # Find player in this CSV
        player_rows = df[df['Player_Normalized'] == player_normalized]

        if len(player_rows) == 0:
            # Player not in this CSV - treat as 0 for combined stats
            if len(stat_config) > 1:
                debug_info.append(f"  • {csv_type}: 0 {column} (not in CSV)")
            continue

        # Get stat value
        try:
            value = float(player_rows.iloc[0][column])
            total += value
            found_any = True
            debug_info.append(f"  • {csv_type}: {value} {column}")
        except (KeyError, ValueError) as e:
            debug_info.append(f"  ⚠️  {csv_type}: Column '{column}' not found or invalid")

    if not found_any:
        return None, debug_info

    return total, debug_info


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def get_pending_parlays(week: int, db_path: Path, include_scored: bool = False) -> List[Dict]:
    """
    Get parlays that need scoring for a specific week.

    Args:
        week: NFL week number
        db_path: Path to SQLite database
        include_scored: If True, include already-scored parlays (for re-scoring)

    Returns:
        List of parlay dictionaries with their legs
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query parlays
    if include_scored:
        query = "SELECT parlay_id, week, confidence_score FROM parlays WHERE week = ?"
    else:
        query = "SELECT parlay_id, week, confidence_score FROM parlays WHERE week = ? AND status = 'pending'"

    parlay_rows = cursor.execute(query, (week,)).fetchall()

    parlays = []
    for parlay_id, week_num, confidence in parlay_rows:
        # Get legs for this parlay
        legs_query = """
            SELECT leg_id, player, team, prop_type, bet_type, line, result
            FROM legs
            WHERE parlay_id = ?
        """
        leg_rows = cursor.execute(legs_query, (parlay_id,)).fetchall()

        legs = []
        for leg_id, player, team, prop_type, bet_type, line, result in leg_rows:
            legs.append({
                'leg_id': leg_id,
                'player': player,
                'team': team,
                'prop_type': prop_type,
                'bet_type': bet_type,
                'line': line,
                'result': result
            })

        parlays.append({
            'parlay_id': parlay_id,
            'week': week_num,
            'confidence': confidence,
            'legs': legs
        })

    conn.close()
    return parlays


def update_parlay_results(
    parlay_id: str,
    leg_results: List[Dict],
    db_path: Path,
    dry_run: bool = False
) -> None:
    """
    Update database with scoring results.

    Args:
        parlay_id: Parlay ID
        leg_results: List of dicts with 'leg_id', 'result', 'actual_value'
        db_path: Path to SQLite database
        dry_run: If True, don't commit changes
    """
    if dry_run:
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Update each leg
    for leg in leg_results:
        cursor.execute(
            """
            UPDATE legs
            SET result = ?, actual_value = ?, scored_date = ?
            WHERE leg_id = ?
            """,
            (leg['result'], leg['actual_value'], datetime.now().isoformat(), leg['leg_id'])
        )

    # Determine overall parlay result
    all_hit = all(leg['result'] == 1 for leg in leg_results if leg['result'] is not None)
    any_miss = any(leg['result'] == 0 for leg in leg_results if leg['result'] is not None)
    any_unscored = any(leg['result'] is None for leg in leg_results)

    if any_unscored:
        status = 'pending'  # Keep as pending if some legs couldn't be scored
    elif all_hit:
        status = 'won'
    else:
        status = 'lost'

    # Update parlay status
    cursor.execute(
        "UPDATE parlays SET status = ? WHERE parlay_id = ?",
        (status, parlay_id)
    )

    conn.commit()
    conn.close()


# ============================================================================
# SCORING LOGIC
# ============================================================================

def score_leg(
    leg: Dict,
    week_stats: Dict[str, pd.DataFrame]
) -> Tuple[Optional[int], Optional[float], List[str]]:
    """
    Score a single parlay leg.

    Args:
        leg: Leg dictionary with player, prop_type, bet_type, line
        week_stats: Loaded CSV data

    Returns:
        (result, actual_value, debug_info)
        - result: 1 (hit), 0 (miss), None (unable to score)
        - actual_value: Actual stat value achieved
        - debug_info: List of debug strings
    """
    player = leg['player']
    prop_type = leg['prop_type']
    bet_type = leg['bet_type']
    line = leg['line']

    # Get stat configuration
    stat_config = STAT_TYPE_MAP.get(prop_type)

    if stat_config is None:
        return None, None, [f"  ⚠️  Unknown prop type: {prop_type}"]

    # Find player's actual stat value
    actual_value, debug_info = find_player_stat(player, stat_config, week_stats)

    if actual_value is None:
        return None, None, debug_info

    # Determine hit/miss
    if bet_type == 'OVER':
        result = 1 if actual_value > line else 0
    elif bet_type == 'UNDER':
        result = 1 if actual_value < line else 0
    else:
        return None, None, [f"  ⚠️  Unknown bet type: {bet_type}"]

    return result, actual_value, debug_info


def score_parlay(
    parlay: Dict,
    week_stats: Dict[str, pd.DataFrame]
) -> Dict:
    """
    Score all legs of a parlay.

    Returns:
        {
            'parlay_id': str,
            'scored_legs': List[Dict],  # leg_id, result, actual_value, debug_info
            'hits': int,
            'total_legs': int,
            'overall_result': 'WIN' | 'LOSS' | 'UNABLE_TO_SCORE'
        }
    """
    scored_legs = []

    for leg in parlay['legs']:
        result, actual_value, debug_info = score_leg(leg, week_stats)

        scored_legs.append({
            'leg_id': leg['leg_id'],
            'player': leg['player'],
            'prop_type': leg['prop_type'],
            'bet_type': leg['bet_type'],
            'line': leg['line'],
            'result': result,
            'actual_value': actual_value,
            'debug_info': debug_info
        })

    # Calculate overall result
    scoreable_legs = [l for l in scored_legs if l['result'] is not None]

    if len(scoreable_legs) == 0:
        overall_result = 'UNABLE_TO_SCORE'
        hits = 0
    else:
        hits = sum(1 for l in scoreable_legs if l['result'] == 1)
        all_legs_scored = len(scoreable_legs) == len(scored_legs)

        if all_legs_scored and hits == len(scored_legs):
            overall_result = 'WIN'
        elif all_legs_scored:
            overall_result = 'LOSS'
        else:
            overall_result = 'PARTIAL'  # Some legs couldn't be scored

    return {
        'parlay_id': parlay['parlay_id'],
        'confidence': parlay['confidence'],
        'scored_legs': scored_legs,
        'hits': hits,
        'total_legs': len(scored_legs),
        'overall_result': overall_result
    }


# ============================================================================
# OUTPUT FORMATTING
# ============================================================================

def format_scoring_results(results: List[Dict], dry_run: bool = False) -> str:
    """Format scoring results for display"""
    lines = []

    lines.append("\n" + "="*70)
    lines.append(f"PARLAY SCORING RESULTS {'(DRY RUN)' if dry_run else ''}")
    lines.append("="*70)

    wins = sum(1 for r in results if r['overall_result'] == 'WIN')
    losses = sum(1 for r in results if r['overall_result'] == 'LOSS')
    partial = sum(1 for r in results if r['overall_result'] == 'PARTIAL')
    unable = sum(1 for r in results if r['overall_result'] == 'UNABLE_TO_SCORE')

    for result in results:
        lines.append(f"\nParlay: {result['parlay_id']} (Confidence: {result['confidence']:.1f}%)")
        lines.append("-" * 70)

        for leg in result['scored_legs']:
            player = leg['player'].title()
            prop = leg['prop_type']
            bet = leg['bet_type']
            line_val = leg['line']
            actual = leg['actual_value']
            hit = leg['result']

            if hit is None:
                # Unable to score
                lines.append(f"  [!] {player}: {prop} {bet} {line_val}")
                lines.append(f"      Player not found in CSV files")
            elif hit == 1:
                # Hit
                lines.append(f"  [HIT] {player}: {prop} {bet} {line_val}")
                lines.append(f"      Actual: {actual:.1f} -> HIT")
            else:
                # Miss
                lines.append(f"  [MISS] {player}: {prop} {bet} {line_val}")
                lines.append(f"      Actual: {actual:.1f} -> MISS")

        # Overall result
        lines.append("")
        if result['overall_result'] == 'WIN':
            lines.append(f"  Result: [WIN] ({result['hits']}/{result['total_legs']} legs hit)")
        elif result['overall_result'] == 'LOSS':
            lines.append(f"  Result: [LOSS] ({result['hits']}/{result['total_legs']} legs hit)")
        elif result['overall_result'] == 'PARTIAL':
            lines.append(f"  Result: [PARTIAL] - some legs unscored ({result['hits']} scored hits)")
        else:
            lines.append(f"  Result: [UNABLE TO SCORE] - no player data found")

    lines.append("\n" + "="*70)
    lines.append("SUMMARY")
    lines.append("="*70)
    lines.append(f"Wins: {wins}")
    lines.append(f"Losses: {losses}")
    if partial > 0:
        lines.append(f"Partial: {partial} (some legs couldn't be scored)")
    if unable > 0:
        lines.append(f"Unable to score: {unable} (no player data)")
    lines.append(f"Total: {len(results)} parlays")

    if dry_run:
        lines.append("\n[INFO] This was a dry run. Run without --dry-run to commit to database.")
    else:
        lines.append("\n[OK] Results saved to database!")

    lines.append("="*70 + "\n")

    return "\n".join(lines)


# ============================================================================
# MAIN SCORING FUNCTION
# ============================================================================

def score_week(
    week: int,
    db_path: Path = None,
    data_dir: Path = None,
    dry_run: bool = True,
    force: bool = False
) -> str:
    """
    Main function to score all parlays for a week.

    Args:
        week: NFL week number
        db_path: Path to SQLite database
        data_dir: Path to data directory
        dry_run: If True, don't commit results to database
        force: If True, re-score already scored parlays

    Returns:
        Formatted string with results
    """
    if db_path is None:
        db_path = Path(__file__).parent / "bets.db"

    if data_dir is None:
        data_dir = Path(__file__).parent / "data"

    # Load week stats
    week_stats = load_week_stats(week, data_dir)

    if not week_stats:
        return f"\n❌ Error: No CSV files found for Week {week}\n"

    # Get parlays to score
    parlays = get_pending_parlays(week, db_path, include_scored=force)

    if not parlays:
        return f"\n[INFO] No {'parlays' if force else 'pending parlays'} found for Week {week}\n"

    print(f"\n[INFO] Found {len(parlays)} parlay{'s' if len(parlays) != 1 else ''} to score")

    # Score each parlay
    results = []
    for parlay in parlays:
        result = score_parlay(parlay, week_stats)
        results.append(result)

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
            update_parlay_results(result['parlay_id'], leg_results, db_path, dry_run=False)

    # Format and return results
    return format_scoring_results(results, dry_run=dry_run)


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Auto-score NFL parlays from weekly CSV files')
    parser.add_argument('--week', type=int, required=True, help='NFL week number (1-18)')
    parser.add_argument('--dry-run', action='store_true', help='Preview scoring without saving to database')
    parser.add_argument('--force', action='store_true', help='Re-score already scored parlays')
    parser.add_argument('--db', type=str, help='Path to database file (default: bets.db)')
    parser.add_argument('--data-dir', type=str, help='Path to data directory (default: ./data)')

    args = parser.parse_args()

    db_path = Path(args.db) if args.db else None
    data_dir = Path(args.data_dir) if args.data_dir else None

    # Default to dry-run unless explicitly executing
    dry_run = args.dry_run or not args.force

    output = score_week(
        week=args.week,
        db_path=db_path,
        data_dir=data_dir,
        dry_run=dry_run,
        force=args.force
    )

    print(output)


if __name__ == "__main__":
    main()
