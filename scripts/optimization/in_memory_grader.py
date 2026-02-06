"""
In-Memory Grader for Fast Weight Optimization

Caches actual stats by week and grades predictions without file I/O.
Returns win/loss counts directly for fast optimization iterations.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import normalize_name function
import importlib.util
spec = importlib.util.spec_from_file_location(
    "data_loader",
    project_root / "scripts" / "analysis" / "data_loader.py"
)
data_loader_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_loader_module)
normalize_name = data_loader_module.normalize_name

logger = logging.getLogger(__name__)


class InMemoryGrader:
    """
    Fast grader that caches actual stats and grades predictions in memory.

    Optimized for weight optimization where we need to grade thousands of
    prediction sets quickly.
    """

    # Mapping bet stat types to internal keys
    STAT_TYPE_MAP = {
        'player_pass_yds': 'pass_yds',
        'player_pass_tds': 'pass_td',
        'player_pass_attempts': 'pass_attempts',
        'player_pass_completions': 'pass_completions',
        'player_rush_yds': 'rush_yds',
        'player_rush_attempts': 'rush_attempts',
        'player_reception_yds': 'rec_yds',
        'player_receptions': 'receptions'
    }

    def __init__(self, data_dir=None):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = data_dir or (self.project_root / "data")

        # Cache of actual stats by week: {week: {player: {stat_key: value}}}
        self._stats_cache: Dict[int, Dict[str, Dict[str, float]]] = {}

    def _load_actual_stats(self, week: int) -> Dict[str, Dict[str, float]]:
        """
        Load actual stats from base files for the given week.
        Returns a dict: {player_name: {stat_type: value}}
        """
        stats_map = {}

        # Map stat types to (file_suffix, column_name)
        files_to_load = [
            (f"wk{week}_passing_base.csv", [
                ('pass_yds', 'YDS'),
                ('pass_td', 'TD'),
                ('pass_attempts', 'ATT'),
                ('pass_completions', 'COM')
            ]),
            (f"wk{week}_rushing_base.csv", [
                ('rush_yds', 'YDS'),
                ('rush_attempts', 'ATT')
            ]),
            (f"wk{week}_receiving_base.csv", [
                ('rec_yds', 'YDS'),
                ('receptions', 'REC')
            ])
        ]

        for filename, mappings in files_to_load:
            fpath = self.data_dir / filename
            if not fpath.exists():
                continue

            try:
                # Robust header detection
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()

                header_row = 0
                for i, line in enumerate(lines):
                    if 'Player' in line and 'Tm' in line:
                        header_row = i
                        break

                df = pd.read_csv(fpath, header=header_row)

                for _, row in df.iterrows():
                    if not isinstance(row.get('Player'), str):
                        continue
                    if 'BASIC' in str(row.get('Player')):
                        continue
                    player = normalize_name(row.get('Player', ''))
                    if not player:
                        continue

                    if player not in stats_map:
                        stats_map[player] = {}

                    for stat_key, col_name in mappings:
                        try:
                            val = row.get(col_name, 0)
                            stats_map[player][stat_key] = float(val)
                        except:
                            stats_map[player][stat_key] = 0.0

            except Exception as e:
                logger.debug(f"Error loading {filename}: {e}")

        return stats_map

    def get_actual_stats(self, week: int) -> Dict[str, Dict[str, float]]:
        """
        Get actual stats for a week (cached).

        Returns:
            Dict mapping player names to their stats
        """
        if week not in self._stats_cache:
            self._stats_cache[week] = self._load_actual_stats(week)
        return self._stats_cache[week]

    def _map_stat_type(self, stat_type_raw: str) -> str:
        """Map prediction stat type to internal key."""
        stat_type_lower = stat_type_raw.lower()

        internal_key = self.STAT_TYPE_MAP.get(stat_type_lower)
        if internal_key:
            return internal_key

        # Fallback fuzzy matching
        if 'pass' in stat_type_lower and 'yds' in stat_type_lower:
            return 'pass_yds'
        elif 'pass' in stat_type_lower and 'td' in stat_type_lower:
            return 'pass_td'
        elif 'pass' in stat_type_lower and 'att' in stat_type_lower:
            return 'pass_attempts'
        elif 'pass' in stat_type_lower and 'comp' in stat_type_lower:
            return 'pass_completions'
        elif 'rush' in stat_type_lower and 'yds' in stat_type_lower:
            return 'rush_yds'
        elif 'rush' in stat_type_lower and 'att' in stat_type_lower:
            return 'rush_attempts'
        elif 'rec' in stat_type_lower and 'yds' in stat_type_lower:
            return 'rec_yds'
        elif 'recep' in stat_type_lower:
            return 'receptions'

        return None

    def grade_predictions(self, predictions: List[Dict], week: int) -> Tuple[int, int, int]:
        """
        Grade predictions against actual stats.

        Args:
            predictions: List of prediction dicts with keys:
                         player_name, stat_type, line, bet_type
            week: Week number to get actual stats

        Returns:
            Tuple of (wins, losses, voids)
        """
        actuals = self.get_actual_stats(week)

        wins = 0
        losses = 0
        voids = 0

        for p in predictions:
            player = normalize_name(p['player_name'])
            stat_type_raw = p['stat_type']
            line = p['line']
            bet_type = p['bet_type']

            internal_key = self._map_stat_type(stat_type_raw)
            if not internal_key:
                voids += 1
                continue

            # Get actual value
            if player not in actuals:
                voids += 1
                continue

            actual_val = actuals[player].get(internal_key, 0.0)

            # Grade the bet
            if bet_type.upper() == 'OVER':
                if actual_val > line:
                    wins += 1
                elif actual_val < line:
                    losses += 1
                else:
                    voids += 1  # Push
            else:  # UNDER
                if actual_val < line:
                    wins += 1
                elif actual_val > line:
                    losses += 1
                else:
                    voids += 1  # Push

        return wins, losses, voids

    def preload_weeks(self, weeks: List[int]):
        """
        Pre-load stats for multiple weeks into cache.
        Useful for optimization to avoid repeated file I/O.
        """
        for week in weeks:
            if week not in self._stats_cache:
                self._stats_cache[week] = self._load_actual_stats(week)
                logger.debug(f"Cached stats for week {week}: {len(self._stats_cache[week])} players")

    def clear_cache(self):
        """Clear the stats cache."""
        self._stats_cache.clear()


if __name__ == "__main__":
    # Demo usage
    grader = InMemoryGrader()

    # Test with a sample week
    stats = grader.get_actual_stats(11)
    print(f"Loaded {len(stats)} players for week 11")

    # Show sample
    for player, player_stats in list(stats.items())[:3]:
        print(f"  {player}: {player_stats}")
