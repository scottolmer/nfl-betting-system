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
        
        recent_perf = context.get('recent_performance', {})
        player_games = recent_perf.get(prop.player_name, [])
        
        if not player_games or len(player_games) < 2:
            rationale.append("⚠️ Insufficient recent data")
            return (50, "AVOID", rationale)
        
        line = prop.line
        
        last_3 = player_games[-3:] if len(player_games) >= 3 else player_games
        hits_over = sum(1 for game in last_3 if game > line)
        last_3_avg = sum(last_3) / len(last_3)
        
        if len(last_3) >= 3 and hits_over == 3:
            score += 25
            rationale.append(f"🔥 HOT STREAK: 3/3 over (avg {last_3_avg:.1f} vs {line})")
        elif hits_over >= 2:
            score += 15
            rationale.append(f"Trending up: {hits_over}/3 over line (avg {last_3_avg:.1f})")
        
        elif hits_over == 0 and len(last_3) >= 3:
            score -= 25
            rationale.append(f"⚠️ COLD: 0/3 over line (avg {last_3_avg:.1f})")
        
        direction = "OVER" if score >= 50 else "UNDER"
        
        if score >= 65:
            rationale.insert(0, f"✅ Strong recent form supports {direction}")
        
        return (score, direction, rationale)
