"""
Game Script Agent - Game flow analysis
"""

from typing import Dict, List, Tuple
from .base_agent import BaseAgent


class GameScriptAgent(BaseAgent):
    """Analyzes game script implications"""
    
    def __init__(self):
        super().__init__(weight=1.3)
    
    def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
        rationale = []
        score = 50
        
        game_total = prop.game_total or 44.5
        spread = prop.spread or 0.0
        
        is_favorite = spread < 0 if prop.is_home else spread > 0
        spread_magnitude = abs(spread)
        
        if game_total >= 51:
            score += 18
            rationale.append(f"🔥 SHOOTOUT expected ({game_total} total)")
            
            if prop.position in ['WR', 'TE', 'QB']:
                score += 7
                rationale.append("Passing volume elevated in shootout")
        
        elif game_total >= 48:
            score += 12
            rationale.append(f"High-scoring game ({game_total} total)")
        
        elif game_total >= 44:
            score += 5
            rationale.append(f"Moderate-scoring game ({game_total} total)")
            if prop.position in ['WR', 'TE', 'QB']:
                score += 3
                rationale.append("Pass-friendly environment expected")
        
        elif game_total <= 40:
            score -= 12
            rationale.append(f"⚠️ Low total ({game_total}) limits opportunities")
            
            if prop.position == 'RB' and 'Rush' in prop.stat_type:
                score += 15
                rationale.append(f"✅ Low total favors RB rushing volume")
        
        if spread_magnitude >= 7:
            if is_favorite:
                if prop.position == 'RB' and 'Rush' in prop.stat_type:
                    score += 12
                    rationale.append(f"Big favorite → clock-killing RB volume")
                elif prop.position in ['WR', 'TE'] and game_total < 48:
                    score -= 8
                    rationale.append(f"⚠️ Big favorite may ease off passing")
            else:
                if prop.position in ['WR', 'TE', 'QB']:
                    score += 15
                    rationale.append(f"Big underdog → pass-heavy game script")
                elif prop.position == 'RB' and 'Rush' in prop.stat_type:
                    score -= 12
                    rationale.append(f"⚠️ Big underdog → limited RB volume")
        
        direction = "OVER" if score >= 50 else "UNDER"
        
        if score >= 65:
            rationale.insert(0, f"✅ Game script strongly favors {direction}")
        
        return (score, direction, rationale)
