"""
Volume Agent - Usage pattern analysis
UPDATED: QB-friendly volume scoring
"""

from typing import Dict, List, Tuple
from .base_agent import BaseAgent


def normalize_player_name(name: str) -> str:
    """Normalize player name for matching"""
    import re
    if not name:
        return name
    name = name.replace('.', '')
    name = re.sub(r'\s+', ' ', name)
    return name.strip().lower()


class VolumeAgent(BaseAgent):
    """Analyzes player usage patterns"""

    def __init__(self, weight: float = 1.2):
        super().__init__(weight=weight)
    
    def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
        rationale = []
        score = 50
        
        usage_data = context.get('usage', {})
        
        # Try normalized name first
        normalized_name = normalize_player_name(prop.player_name)
        player_usage = usage_data.get(normalized_name)
        
        # Try original name lowercase as fallback
        if not player_usage:
            player_usage = usage_data.get(prop.player_name.lower(), {})
        
        if not player_usage:
            rationale.append("⚠️ Limited usage data")
            return (50, "AVOID", rationale)
        
        if prop.position == 'QB':
            # QB: Check snap share (primary starter indicator)
            snap_share = player_usage.get('snap_share_pct', 0)
            
            if snap_share >= 90:
                score += 15
                rationale.append(f"💪 Elite starter: {snap_share:.1f}% snaps")
            elif snap_share >= 75:
                score += 10
                rationale.append(f"Strong starter: {snap_share:.1f}% snaps")
            elif snap_share >= 50:
                score += 5
                rationale.append(f"Regular starter: {snap_share:.1f}% snaps")
            elif snap_share < 30:
                score -= 15
                rationale.append(f"⚠️ Limited role: {snap_share:.1f}% snaps")
            
            # Check for pass attempts if available
            pass_attempts = player_usage.get('pass_attempts', 0)
            if pass_attempts > 0:
                if pass_attempts >= 40:
                    score += 8
                    rationale.append(f"High volume: {pass_attempts:.0f} attempts")
                elif pass_attempts < 15:
                    score -= 8
                    rationale.append(f"Low volume: {pass_attempts:.0f} attempts")
        
        elif prop.position in ['WR', 'TE']:
            # WR/TE: Target share is crucial metric
            target_share = player_usage.get('target_share_pct', 0)
            
            if target_share >= 28:
                score += 22
                rationale.append(f"🎯 ELITE VOLUME: {target_share:.1f}% targets")
            elif target_share >= 22:
                score += 15
                rationale.append(f"🎯 High volume: {target_share:.1f}% targets")
            elif target_share >= 15:
                score += 8
                rationale.append(f"Solid volume: {target_share:.1f}% targets")
            elif target_share < 10:
                score -= 15
                rationale.append(f"⚠️ LOW VOLUME: Only {target_share:.1f}% targets")
        
        elif prop.position == 'RB':
            # RB: Check snap share, touch share, and rushing attempts
            snap_share = player_usage.get('snap_share_pct', 0)
            rush_attempts = player_usage.get('rush_attempts', 0)
            touch_pct = player_usage.get('touch_pct', 0)
            rush_attempt_pct = player_usage.get('rush_attempt_pct', 0)

            # Snap share analysis
            if snap_share >= 75:
                score += 22
                rationale.append(f"🔒 BELLCOW: {snap_share:.1f}% snaps")
            elif snap_share >= 60:
                score += 12
                rationale.append(f"Lead back: {snap_share:.1f}% snaps")
            elif snap_share < 35:
                score -= 18
                rationale.append(f"⚠️ LIMITED ROLE: {snap_share:.1f}% snaps")

            # Touch share analysis (very important for RBs)
            if touch_pct >= 50:
                score += 10
                rationale.append(f"🎯 High touch share: {touch_pct:.1f}%")
            elif touch_pct >= 35:
                score += 5
                rationale.append(f"Good touch share: {touch_pct:.1f}%")
            elif touch_pct > 0 and touch_pct < 25:
                score -= 10
                rationale.append(f"⚠️ Low touch share: {touch_pct:.1f}%")

            # Rush attempt percentage (team share of carries)
            if rush_attempt_pct >= 70:
                score += 8
                rationale.append(f"Workhorse: {rush_attempt_pct:.1f}% of team carries")
            elif rush_attempt_pct >= 50:
                score += 4
                rationale.append(f"Primary back: {rush_attempt_pct:.1f}% of team carries")

            # Check rush attempts for rushing props
            if 'Rush' in prop.stat_type and rush_attempts >= 18:
                score += 8
                rationale.append(f"Elite volume: {rush_attempts:.0f} attempts/game")
            elif 'Rush' in prop.stat_type and rush_attempts >= 12:
                score += 4
                rationale.append(f"Good volume: {rush_attempts:.0f} attempts/game")
        
        # Trend analysis - same for all positions
        trend = player_usage.get('trend', 'stable')
        if trend == 'increasing':
            score += 10
            rationale.append("📈 Usage trending UP")
        elif trend == 'decreasing':
            score -= 10
            rationale.append("📉 Usage trending DOWN")
        
        direction = "OVER" if score >= 50 else "UNDER"
        
        if score >= 70:
            rationale.insert(0, f"✅ Volume strongly supports {direction}")
        
        return (score, direction, rationale)
