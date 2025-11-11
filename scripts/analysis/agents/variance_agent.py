"""
Variance Agent - Prop reliability
"""

from typing import Dict, List, Tuple
from .base_agent import BaseAgent


class VarianceAgent(BaseAgent):
    """Evaluates prop type reliability"""
    
    def __init__(self):
        super().__init__(weight=1.5)
    
    def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
        rationale = []
        score = 50
        
        stat_type = prop.stat_type
        position = prop.position
        
        if position == 'QB':
            if 'Pass Yds' in stat_type:
                score += 12
                rationale.append("✓✓ Pass yards: high reliability")
            elif 'Pass Attempts' in stat_type:
                score += 10
                rationale.append("✓✓ Pass attempts: high reliability")
            elif 'Pass Completions' in stat_type:
                score += 8
                rationale.append("✓ Pass completions: good reliability")
            elif 'TD' in stat_type:
                score -= 8
                rationale.append("⚠️ Passing TD: moderate variance")
        
        elif position in ['WR', 'TE']:
            if 'Rec Yds' in stat_type:
                score += 5
                rationale.append("✓ Receiving yards: moderate reliability")
            elif 'Receptions' in stat_type:
                score += 8
                rationale.append("✓✓ Reception props: high reliability")
            elif 'TD' in stat_type:
                score -= 10
                rationale.append("⚠️ TD props: high variance")
        
        elif position == 'RB':
            if 'Rush Yds' in stat_type:
                score += 3
                rationale.append("✓ Rushing yards: moderate reliability")
            elif 'TD' in stat_type:
                score -= 10
                rationale.append("⚠️ TD props: high variance")
        
        direction = "OVER" if score >= 50 else "UNDER"
        return (score, direction, rationale)
