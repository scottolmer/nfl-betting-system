"""
Trend Agent - Recent performance analysis with Regression to Mean logic
"""

from typing import Dict, List, Tuple
from .base_agent import BaseAgent
import logging

class TrendAgent(BaseAgent):
    """
    Analyzes recent performance trends - FADE THE HEAT only.

    Based on backtesting (weeks 11-16, 2294 samples):
    - "Fade hot players" (trending UP → UNDER) hit at 58.7%
    - "Buy the dip" (trending DOWN → OVER) only hit at 21.7% - REMOVED

    Current logic:
    - Players trending UP in usage → Bet UNDER (lines are inflated)
    - Players trending DOWN or stable → NEUTRAL (no edge identified)
    """

    def __init__(self, weight: float = 1.0):
        super().__init__(weight=weight)
        if not hasattr(self, 'logger') or self.logger is None:
             self.logger = logging.getLogger(self.__class__.__name__)
    
    def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
        rationale = []
        score = 50
        
        # NOTE: WE NOW ANALYZE ALL PROPS, including Volume.
        # Previously we skipped volume props, which was a mistake.
        
        trends = context.get('trends', {})
        player_name = prop.player_name.lower()
        player_trend = trends.get(player_name, {})
        
        if not player_trend:
            # No specific trend data
            return (50, "AVOID", [])
        
        # Determine which trend metric to use based on position
        trend_key = None
        if prop.position == 'QB':
            # For QBs, we care about passing volume trends if possible, or snap share?
            # Data loader mostly tracks snap/target share. 
            # DVOA loader aggregates data. let's look for attempts/yards trends if available?
            # For now, stick to the keys populated by stats_aggregator
            trend_key = 'snap_share_pct_trend' 
            # Or if stats_aggregator calculates 'pass_yds_trend', we could use that.
            # Looking at stats_aggregator: it calculates '{stat}_trend' for what it finds.
            # Let's rely on the generic trends found.
        elif prop.position in ['WR', 'TE']:
            trend_key = 'target_share_pct_trend'
        elif prop.position == 'RB':
            trend_key = 'snap_share_pct_trend'
            
        # Fallback to looking for stat-specific trends if the general usage trend is missing
        # prop.stat_type could be 'Rush Yds'. stats_aggregator makes 'rush_yds_trend'
        specific_trend_key = f"{prop.stat_type.lower().replace(' ', '_')}_trend"
        
        # Priority: Usage Trend > Output Trend (Output is noisier)
        trend_direction = player_trend.get(trend_key, 'stable') if trend_key else 'stable'
        
        # If usage is stable, check specific stat trend (e.g. Yards trending up while usage stable = Efficiency spike? -> Sustain or Fade?)
        # For simplicity in V2: We stick to the "Fade the Trend" philosophy.
        
        if trend_direction == 'increasing':
            # Trend is UP. Public is buying. Line is likely inflated.
            # FADE THE HEAT - this signal hits at 58.7% historically
            score = 30  # Strong UNDER signal
            rationale.append(f"📉 FADING HEAT: Usage trending UP (line likely inflated)")
            direction = "UNDER"
        elif trend_direction == 'decreasing':
            # Trend is DOWN.
            # NOTE: "Buy the dip" was hitting only 21.7% - players trending down stay down.
            # Return neutral - no edge identified.
            score = 50
            rationale.append(f"⚖️ Usage trending DOWN (no edge - staying neutral)")
            direction = "NEUTRAL"
        else:
            # Stable trend - no signal
            score = 50
            rationale.append(f"⚖️ Stable usage trend (no signal)")
            direction = "NEUTRAL"
        
        return (score, direction, rationale)
