"""
Volume Agent - Usage pattern analysis (FIXED IMPORTS)
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
    
    def __init__(self):
        super().__init__(weight=1.2)
    
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
        
        if prop.position in ['WR', 'TE']:
            target_share = player_usage.get('target_share_pct', 0)
            
            if target_share >= 28:
                score += 25
                rationale.append(f"🎯 ELITE VOLUME: {target_share:.1f}% target share")
            elif target_share >= 22:
                score += 18
                rationale.append(f"🎯 High volume: {target_share:.1f}% targets")
            elif target_share >= 15:
                score += 10
                rationale.append(f"Solid volume: {target_share:.1f}% target share")
            elif target_share < 10:
                score -= 18
                rationale.append(f"⚠️ LOW VOLUME: Only {target_share:.1f}% targets")
        
        elif prop.position == 'RB':
            snap_share = player_usage.get('snap_share_pct', 0)
            
            if snap_share >= 75:
                score += 25
                rationale.append(f"🔒 BELLCOW: {snap_share:.1f}% snaps")
            elif snap_share >= 60:
                score += 15
                rationale.append(f"Lead back: {snap_share:.1f}% snaps")
            elif snap_share < 35:
                score -= 20
                rationale.append(f"⚠️ LIMITED ROLE: {snap_share:.1f}% snaps")
        
        trend = player_usage.get('trend', 'stable')
        if trend == 'increasing':
            score += 10
            rationale.append("📈 Usage trending UP")
        elif trend == 'decreasing':
            score -= 10
            rationale.append("📉 Usage trending DOWN")
        
        direction = "OVER" if score >= 50 else "UNDER"
        
        if score >= 70:
            rationale.insert(0, f"✅ Elite volume supports {direction}")
        
        return (score, direction, rationale)
