"""
Trend Agent - Recent performance analysis
"""

from typing import Dict, List, Tuple
from .base_agent import BaseAgent


class TrendAgent(BaseAgent):
    """Analyzes recent performance trends"""
    
    def __init__(self):
        super().__init__(weight=1.0)
    
    def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
        rationale = []
        score = 50
        
        trends = context.get('trends', {})
        player_name = prop.player_name.lower()
        player_trend = trends.get(player_name, {})
        
        if not player_trend:
            rationale.append("⚠️ Insufficient trend data")
            return (50, "AVOID", rationale)
        
        # Determine which trend metric based on position
        trend_key = None
        if prop.position == 'QB':
            trend_key = 'snap_share_pct_trend'
        elif prop.position in ['WR', 'TE']:
            trend_key = 'target_share_pct_trend' if 'Rec' in prop.stat_type else 'rec_yds_trend'
        elif prop.position == 'RB':
            trend_key = 'snap_share_pct_trend' if 'Rush' in prop.stat_type else 'rec_yds_trend'
        
        trend_direction = player_trend.get(trend_key, 'stable') if trend_key else 'stable'
        
        if trend_direction == 'increasing':
            score += 15
            rationale.append(f"💶 Usage trending UP")
        elif trend_direction == 'decreasing':
            score -= 15
            rationale.append(f"💹 Usage trending DOWN")
        else:
            score += 5  # Stable is slightly positive
            rationale.append(f"⚖️ Stable, consistent trend")
        
        direction = "OVER" if score >= 50 else "UNDER"
        
        if score >= 65:
            rationale.insert(0, f"✅ Strong trend supports {direction}")
        elif score <= 35:
            rationale.insert(0, f"⚠️ Negative trend indicates {direction}")
        
        return (score, direction, rationale)
