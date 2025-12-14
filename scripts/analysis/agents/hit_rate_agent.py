"""
Hit Rate Agent - Analyzes how often a player goes over/under a specific line
"""

from typing import Dict, List, Tuple, Optional
from .base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)


class HitRateAgent(BaseAgent):
    """
    Analyzes historical performance vs. the specific betting line

    Looks at previous weeks to determine hit rate:
    - If player has gone OVER the line 7/10 times → high confidence OVER
    - If player has gone UNDER the line 8/10 times → high confidence UNDER
    """

    def __init__(self, weight: float = 2.0):
        """
        Initialize Hit Rate Agent

        Args:
            weight: Agent weight (default 2.0 - significant signal from historical performance)
        """
        super().__init__(weight=weight)

    def analyze(self, prop, context: Dict) -> Optional[Tuple[float, str, List[str]]]:
        """
        Analyze hit rate for the prop

        Returns:
            (score, direction, rationale) or None if insufficient data
        """
        rationale = []

        # Map stat types to data file columns
        stat_mapping = {
            'Receptions': ('receiving_base', 'REC'),
            'Rec Yds': ('receiving_base', 'YDS'),
            'Rush Yds': ('rushing_base', 'YDS'),
            'Rush Att': ('rushing_base', 'ATT'),
            'Pass Yds': ('passing_base', 'YDS'),
            'Completions': ('passing_base', 'COM'),
            'Pass Att': ('passing_base', 'ATT'),
            'Pass TDs': ('passing_base', 'TD'),
            'Rush TDs': ('rushing_base', 'TD'),
            'Rec TDs': ('receiving_base', 'TD'),
        }

        # Get the appropriate data file and column
        stat_info = stat_mapping.get(prop.stat_type)
        if not stat_info:
            # Stat type not supported for hit rate analysis
            return None

        data_file, column_name = stat_info

        # Get historical stats
        historical_stats = context.get('historical_stats', {})
        if not historical_stats:
            rationale.append("⚠️ No historical data available")
            return None

        # Collect player's performance across recent weeks
        # Normalize player name: lowercase, strip, and collapse multiple spaces
        import re
        player_name_lower = re.sub(r'\s+', ' ', prop.player_name.lower().strip())
        weekly_values = []

        for week_key in sorted(historical_stats.keys()):
            week_data = historical_stats[week_key]
            if data_file not in week_data:
                continue

            df = week_data[data_file]

            # Normalize player names for matching (collapse multiple spaces)
            df['Player_Normalized'] = df['Player'].str.lower().str.strip().str.replace(r'\s+', ' ', regex=True)

            # Find player's row
            player_row = df[df['Player_Normalized'] == player_name_lower]

            if not player_row.empty and column_name in player_row.columns:
                value = player_row.iloc[0][column_name]
                try:
                    weekly_values.append(float(value))
                except (ValueError, TypeError):
                    continue

        # Need at least 3 games to make a meaningful assessment
        if len(weekly_values) < 3:
            rationale.append(f"⚠️ Only {len(weekly_values)} games available (need 3+)")
            return None

        # Calculate hit rate
        line = prop.line
        over_count = sum(1 for val in weekly_values if val > line)
        under_count = sum(1 for val in weekly_values if val < line)
        push_count = sum(1 for val in weekly_values if val == line)
        total_games = len(weekly_values)

        over_rate = (over_count / total_games) * 100
        under_rate = (under_count / total_games) * 100

        # Calculate confidence score based on hit rate
        # Hit rate above 70% → strong signal
        # Hit rate 60-70% → moderate signal
        # Hit rate 50-60% → weak signal
        # Hit rate below 50% → opposite direction

        if over_rate >= 70:
            score = 70 + (over_rate - 70) * 0.5  # 70-85 score range for 70-100% hit rate
            direction = "OVER"
            rationale.append(f"✅ Hit OVER in {over_count}/{total_games} games ({over_rate:.0f}%)")
        elif over_rate >= 60:
            score = 60 + (over_rate - 60)  # 60-70 score range
            direction = "OVER"
            rationale.append(f"💚 Hit OVER in {over_count}/{total_games} games ({over_rate:.0f}%)")
        elif under_rate >= 70:
            score = 30 - (under_rate - 70) * 0.5  # 15-30 score range for 70-100% under rate
            direction = "UNDER"
            rationale.append(f"✅ Hit UNDER in {under_count}/{total_games} games ({under_rate:.0f}%)")
        elif under_rate >= 60:
            score = 40 - (under_rate - 60)  # 30-40 score range
            direction = "UNDER"
            rationale.append(f"💚 Hit UNDER in {under_count}/{total_games} games ({under_rate:.0f}%)")
        else:
            # Mixed results - slight lean based on which side is higher
            if over_rate > under_rate:
                score = 50 + (over_rate - under_rate) * 0.3
                direction = "OVER"
                rationale.append(f"⚖️ Inconsistent: {over_count}O/{under_count}U/{push_count}P in {total_games} games")
            else:
                score = 50 - (under_rate - over_rate) * 0.3
                direction = "UNDER"
                rationale.append(f"⚖️ Inconsistent: {over_count}O/{under_count}U/{push_count}P in {total_games} games")

        # Add recent performance context (last 3 games)
        recent_values = weekly_values[-3:]
        recent_over = sum(1 for val in recent_values if val > line)
        recent_under = sum(1 for val in recent_values if val < line)

        if recent_over == 3:
            score += 5
            rationale.append(f"🔥 3-game hot streak (all OVER)")
        elif recent_under == 3:
            score -= 5
            rationale.append(f"❄️ 3-game cold streak (all UNDER)")

        # Show actual values for transparency
        values_str = ", ".join([f"{v:.1f}" for v in weekly_values[-5:]])  # Last 5 games
        rationale.append(f"📊 Last {min(5, len(weekly_values))} games: {values_str} (line: {line})")

        # Clamp score to valid range
        score = max(0, min(100, score))

        return (score, direction, rationale)
