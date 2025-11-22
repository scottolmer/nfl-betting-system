"""
Weekly Parlay Export for Calibration
Exports all parlays generated for a specific week to CSV for manual Win/Loss entry.
Implements "mark everything" philosophy to maximize learning data.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import logging
import json

from .parlay_tracker import ParlayTracker
from .performance_tracker import PerformanceTracker

logger = logging.getLogger(__name__)


class WeeklyParlayExporter:
    """
    Exports all parlays for a given week to CSV format for calibration.
    One row per parlay leg with all agent scores and confidence data.
    """

    def __init__(
        self,
        tracker: Optional[ParlayTracker] = None,
        perf_tracker: Optional[PerformanceTracker] = None,
        output_dir: str = "data/calibration",
        db_path: str = "bets.db"
    ):
        """
        Initialize the exporter.

        Args:
            tracker: ParlayTracker instance (creates new one if None)
            perf_tracker: PerformanceTracker instance (creates new one if None)
            output_dir: Directory to save calibration CSV files
            db_path: Path to SQLite database for PerformanceTracker
        """
        self.tracker = tracker or ParlayTracker()
        self.perf_tracker = perf_tracker or PerformanceTracker(db_path=db_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_week(self, week: int, year: int = 2024, overwrite: bool = False) -> Optional[str]:
        """
        Export all parlays for a specific week to CSV.

        Args:
            week: NFL week number (1-18)
            year: Season year
            overwrite: If True, overwrite existing file without prompting

        Returns:
            File path if successful, None otherwise
        """
        print(f"\n{'=' * 80}")
        print(f"EXPORT: EXPORTING PARLAYS FOR WEEK {week} ({year})")
        print(f"{'=' * 80}\n")

        # Load parlays from BOTH sources
        print(f"Loading week {week} parlays from tracking systems...")

        # Source 1: JSON tracker (custom + some system parlays)
        json_parlays = self.tracker.get_parlays_by_week(week, year)
        print(f"  - Found {len(json_parlays)} parlays in JSON tracker")

        # Source 2: SQLite database (optimized system parlays)
        sqlite_parlays = self._load_parlays_from_sqlite(week, year)
        print(f"  - Found {len(sqlite_parlays)} parlays in SQLite database")

        # Merge parlays (avoid duplicates by parlay_id)
        parlays = self._merge_parlays(json_parlays, sqlite_parlays)

        if not parlays:
            print(f"\n[ERROR] No parlays found for week {week} ({year})")
            print(f"   Make sure you've run analysis for this week first.")
            return None

        # Categorize parlays
        system_parlays = [p for p in parlays if p.get('parlay_type') in ['traditional', 'enhanced', 'generated']]
        custom_parlays = [p for p in parlays if p.get('parlay_type') == 'custom']
        bet_parlays = [p for p in parlays if p.get('bet_on', False)]

        print(f"\nTotal parlays after merging: {len(parlays)}")
        print(f"  - {len(system_parlays)} system parlays")
        print(f"  - {len(custom_parlays)} custom parlays")
        print(f"  - {len(bet_parlays)} parlays actually bet on\n")

        # Convert parlays to leg-level rows
        print("Converting parlays to individual legs...")
        rows = []
        total_legs = 0

        for parlay_idx, parlay in enumerate(parlays, 1):
            parlay_id = parlay.get('parlay_id', f'unknown_{parlay_idx}')
            parlay_type = parlay.get('parlay_type', 'unknown')
            was_bet = parlay.get('bet_on', False)
            props = parlay.get('props', [])
            correlations = parlay.get('correlations', [])

            # Get correlation adjustment (if available)
            correlation_adjustment = 0
            if correlations:
                # Try to extract correlation adjustment
                for corr in correlations:
                    if isinstance(corr, dict):
                        correlation_adjustment = corr.get('adjustment', 0)
                        break

            # Process each leg (prop) in the parlay
            for leg_idx, prop in enumerate(props, 1):
                total_legs += 1

                # Extract base prop data
                player_name = prop.get('player', 'Unknown')
                position = prop.get('position', 'Unknown')
                team = prop.get('team', 'Unknown')
                opponent = prop.get('opponent', 'Unknown')
                stat_type = prop.get('stat_type', 'Unknown')
                line = prop.get('line', 0)
                direction = prop.get('direction', 'OVER')
                confidence = prop.get('confidence', 0)

                # Determine home/away (default to UNKNOWN if not specified)
                home_away = "UNKNOWN"
                if 'is_home' in prop:
                    home_away = "HOME" if prop['is_home'] else "AWAY"

                # Extract agent scores
                agent_scores = prop.get('agent_scores', {})

                # Handle both formats: old style (raw scores) and new style (with raw_score/weight)
                dvoa_score = self._extract_agent_score(agent_scores, 'DVOA')
                matchup_score = self._extract_agent_score(agent_scores, 'Matchup')
                volume_score = self._extract_agent_score(agent_scores, 'Volume')
                injury_score = self._extract_agent_score(agent_scores, 'Injury')
                trend_score = self._extract_agent_score(agent_scores, 'Trend')
                gamescript_score = self._extract_agent_score(agent_scores, 'GameScript')
                variance_score = self._extract_agent_score(agent_scores, 'Variance')
                weather_score = self._extract_agent_score(agent_scores, 'Weather')

                # Calculate raw confidence (before correlation adjustment)
                # For custom parlays, raw_confidence might be in parlay data
                raw_confidence = parlay.get('raw_confidence', confidence)
                adjusted_confidence = parlay.get('effective_confidence', confidence)

                # Build row
                row = {
                    'week': week,
                    'year': year,
                    'parlay_id': parlay_id,
                    'leg_number': leg_idx,
                    'parlay_type': parlay_type,
                    'was_bet_on': was_bet,
                    'player_name': player_name,
                    'position': position,
                    'team': team,
                    'opponent': opponent,
                    'home_away': home_away,
                    'prop_type': stat_type,
                    'line': line,
                    'prediction': direction,
                    'leg_confidence': confidence,
                    'parlay_raw_confidence': raw_confidence,
                    'correlation_adjustment': correlation_adjustment,
                    'parlay_adjusted_confidence': adjusted_confidence,
                    'dvoa_score': dvoa_score,
                    'matchup_score': matchup_score,
                    'volume_score': volume_score,
                    'injury_score': injury_score,
                    'trend_score': trend_score,
                    'gamescript_score': gamescript_score,
                    'variance_score': variance_score,
                    'weather_score': weather_score,
                    'bet_result': ''  # Empty for user to fill in
                }

                rows.append(row)

        print(f"[OK] Converted {len(parlays)} parlays into {total_legs} individual legs\n")

        # Create DataFrame
        df = pd.DataFrame(rows)

        # Generate filename
        filename = f"week_{week}_{year}_parlays.csv"
        filepath = self.output_dir / filename

        # Check if file exists
        if filepath.exists() and not overwrite:
            print(f"[WARNING]  File already exists: {filepath}")
            response = input("Overwrite? (y/n): ").strip().lower()
            if response != 'y':
                print("[ERROR] Export cancelled")
                return None

        # Save to CSV
        df.to_csv(filepath, index=False)

        # Print summary
        print(f"{'=' * 80}")
        print(f"[SUCCESS] EXPORT SUCCESSFUL")
        print(f"{'=' * 80}")
        print(f"File: {filepath}")
        print(f"Total parlays: {len(parlays)}")
        print(f"Total legs exported: {total_legs}")
        print(f"Columns: {len(df.columns)}")
        print(f"\nNOTE: Next steps:")
        print(f"  1. Open the CSV file in Excel/Google Sheets")
        print(f"  2. Fill in the 'bet_result' column with W (win) or L (loss) for each leg")
        print(f"  3. Save the file")
        print(f"  4. Run calibration analysis to adjust agent weights")
        print(f"{'=' * 80}\n")

        return str(filepath)

    def _extract_agent_score(self, agent_scores: Dict, agent_name: str) -> float:
        """
        Extract agent score from agent_scores dict.
        Handles both old format (direct scores) and new format (with raw_score/weight).

        Args:
            agent_scores: Dictionary of agent scores
            agent_name: Name of the agent

        Returns:
            Agent score (0-10 scale) or 0 if not found
        """
        if not agent_scores or agent_name not in agent_scores:
            return 0.0

        score_data = agent_scores[agent_name]

        # New format: {'raw_score': 78, 'weight': 0.20}
        if isinstance(score_data, dict):
            raw_score = score_data.get('raw_score', 0)
            # Convert 0-100 scale to 0-10 scale
            return round(raw_score / 10.0, 1) if raw_score > 0 else 0.0

        # Old format: direct score value
        if isinstance(score_data, (int, float)):
            # Assume it's already on 0-10 scale
            return round(float(score_data), 1)

        return 0.0

    def _load_parlays_from_sqlite(self, week: int, year: int = 2024) -> List[Dict]:
        """
        Load parlays from SQLite PerformanceTracker database.

        Args:
            week: NFL week number
            year: Season year

        Returns:
            List of parlay dictionaries in JSON tracker format
        """
        import sqlite3

        parlays = []

        try:
            # Query parlays from SQLite
            cursor = self.perf_tracker.conn.cursor()
            query = """
                SELECT parlay_id, confidence_score, parlay_type, agent_breakdown, created_date
                FROM parlays
                WHERE week = ?
                ORDER BY created_timestamp
            """
            results = cursor.execute(query, (week,)).fetchall()

            for parlay_id, confidence, parlay_type, agent_breakdown_json, created_date in results:
                # Get legs for this parlay
                legs_query = """
                    SELECT player, team, prop_type, bet_type, line, agent_scores
                    FROM legs
                    WHERE parlay_id = ?
                """
                legs = cursor.execute(legs_query, (parlay_id,)).fetchall()

                # Convert to JSON tracker format
                props = []
                for player, team, prop_type, bet_type, line, agent_scores_json in legs:
                    try:
                        agent_scores = json.loads(agent_scores_json) if agent_scores_json else {}
                    except:
                        agent_scores = {}

                    props.append({
                        'player': player,
                        'team': team,
                        'opponent': 'Unknown',  # Not stored in SQLite
                        'position': 'Unknown',  # Not stored in SQLite
                        'stat_type': prop_type,
                        'line': line,
                        'direction': bet_type,
                        'confidence': confidence * 100 if confidence < 1 else confidence,  # Convert 0-1 to 0-100
                        'is_home': None,
                        'agent_scores': agent_scores
                    })

                # Parse agent breakdown
                try:
                    agent_breakdown = json.loads(agent_breakdown_json) if agent_breakdown_json else {}
                except:
                    agent_breakdown = {}

                # Create parlay dict in JSON tracker format
                parlay_dict = {
                    'parlay_id': parlay_id,
                    'week': week,
                    'year': year,
                    'parlay_type': parlay_type or 'generated',
                    'props': props,
                    'raw_confidence': confidence * 100 if confidence < 1 else confidence,
                    'effective_confidence': confidence * 100 if confidence < 1 else confidence,
                    'correlations': [],
                    'bet_on': False,
                    'agent_breakdown': agent_breakdown,
                    'generated_timestamp': created_date
                }

                parlays.append(parlay_dict)

        except Exception as e:
            logger.error(f"Error loading parlays from SQLite: {e}")
            # Don't fail the whole export, just log and continue

        return parlays

    def _merge_parlays(self, json_parlays: List[Dict], sqlite_parlays: List[Dict]) -> List[Dict]:
        """
        Merge parlays from JSON and SQLite sources, avoiding duplicates.

        Args:
            json_parlays: Parlays from JSON tracker
            sqlite_parlays: Parlays from SQLite database

        Returns:
            Combined list without duplicates
        """
        # Use parlay_id as key to avoid duplicates
        seen_ids = set()
        merged = []

        # Add JSON parlays first (these are authoritative)
        for parlay in json_parlays:
            parlay_id = parlay.get('parlay_id')
            if parlay_id and parlay_id not in seen_ids:
                seen_ids.add(parlay_id)
                merged.append(parlay)

        # Add SQLite parlays that aren't already in JSON
        for parlay in sqlite_parlays:
            parlay_id = parlay.get('parlay_id')
            if parlay_id and parlay_id not in seen_ids:
                seen_ids.add(parlay_id)
                merged.append(parlay)

        return merged

    def get_available_weeks(self, year: int = 2024) -> List[int]:
        """
        Get list of weeks that have parlays available for export.

        Args:
            year: Season year

        Returns:
            List of week numbers with available parlays
        """
        weeks_tracked = self.tracker.data.get('metadata', {}).get('weeks_tracked', [])
        # Filter by year
        available_weeks = []
        for week in weeks_tracked:
            parlays = self.tracker.get_parlays_by_week(week, year)
            if parlays:
                available_weeks.append(week)
        return sorted(available_weeks)

    def export_all_weeks(self, year: int = 2024, overwrite: bool = False) -> List[str]:
        """
        Export all weeks that have parlays.

        Args:
            year: Season year
            overwrite: If True, overwrite existing files without prompting

        Returns:
            List of file paths created
        """
        available_weeks = self.get_available_weeks(year)

        if not available_weeks:
            print(f"[ERROR] No weeks with parlays found for {year}")
            return []

        print(f"\n{'=' * 80}")
        print(f"EXPORT: EXPORTING ALL AVAILABLE WEEKS FOR {year}")
        print(f"{'=' * 80}")
        print(f"Found parlays for weeks: {', '.join(map(str, available_weeks))}\n")

        exported_files = []
        for week in available_weeks:
            filepath = self.export_week(week, year, overwrite=overwrite)
            if filepath:
                exported_files.append(filepath)
            print()  # Add spacing between exports

        print(f"\n{'=' * 80}")
        print(f"[SUCCESS] BATCH EXPORT COMPLETE")
        print(f"{'=' * 80}")
        print(f"Exported {len(exported_files)} weeks:")
        for filepath in exported_files:
            print(f"  - {filepath}")
        print(f"{'=' * 80}\n")

        return exported_files

    def preview_week(self, week: int, year: int = 2024, num_rows: int = 10) -> None:
        """
        Preview what will be exported for a week without saving to file.

        Args:
            week: NFL week number
            year: Season year
            num_rows: Number of rows to display (default 10)
        """
        print(f"\n{'=' * 80}")
        print(f"PREVIEW: Week {week} ({year}) Export")
        print(f"{'=' * 80}\n")

        parlays = self.tracker.get_parlays_by_week(week, year)

        if not parlays:
            print(f"[ERROR] No parlays found for week {week} ({year})")
            return

        print(f"Found {len(parlays)} parlays")
        print(f"Preview of first {num_rows} legs:\n")

        # Build preview rows
        rows = []
        for parlay in parlays[:3]:  # Show first 3 parlays
            for prop in parlay.get('props', [])[:num_rows]:
                rows.append({
                    'Parlay ID': parlay.get('parlay_id', 'N/A'),
                    'Player': prop.get('player', 'N/A'),
                    'Prop': f"{prop.get('stat_type', 'N/A')} {prop.get('direction', 'N/A')} {prop.get('line', 0)}",
                    'Confidence': f"{prop.get('confidence', 0)}%",
                    'Type': parlay.get('parlay_type', 'N/A')
                })
                if len(rows) >= num_rows:
                    break
            if len(rows) >= num_rows:
                break

        if rows:
            df = pd.DataFrame(rows)
            print(df.to_string(index=False))

        print(f"\n{'=' * 80}\n")


def export_weekly_parlays(week: int, year: int = 2024, overwrite: bool = False) -> Optional[str]:
    """
    Convenience function to export parlays for a specific week.

    Args:
        week: NFL week number (1-18)
        year: Season year
        overwrite: If True, overwrite existing file without prompting

    Returns:
        File path if successful, None otherwise
    """
    exporter = WeeklyParlayExporter()
    return exporter.export_week(week, year, overwrite)


def export_all_parlays(year: int = 2024, overwrite: bool = False) -> List[str]:
    """
    Convenience function to export all available weeks.

    Args:
        year: Season year
        overwrite: If True, overwrite existing files without prompting

    Returns:
        List of file paths created
    """
    exporter = WeeklyParlayExporter()
    return exporter.export_all_weeks(year, overwrite)


def preview_weekly_parlays(week: int, year: int = 2024, num_rows: int = 10) -> None:
    """
    Convenience function to preview what will be exported.

    Args:
        week: NFL week number
        year: Season year
        num_rows: Number of rows to display
    """
    exporter = WeeklyParlayExporter()
    exporter.preview_week(week, year, num_rows)
