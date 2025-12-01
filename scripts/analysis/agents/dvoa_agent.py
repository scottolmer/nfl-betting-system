"""
DVOA Agent - Analyzes team efficiency
UPDATED: QB-friendly scoring with fair WR/TE competition
"""

from typing import Dict, List, Tuple
from .base_agent import BaseAgent


class DVOAAgent(BaseAgent):
    """Analyzes matchups using DVOA"""

    def __init__(self, weight: float = 2.0):
        super().__init__(weight=weight)
    
    def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
        rationale = []
        score = 50
        
        off_dvoa = context.get('dvoa_offensive', {})
        def_dvoa = context.get('dvoa_defensive', {})
        
        team_off = off_dvoa.get(prop.team, {})
        opp_def = def_dvoa.get(prop.opponent, {})
        
        if not team_off or not opp_def:
            rationale.append("⚠️ DVOA data not available")
            return (50, "AVOID", rationale)
        
        total_off_dvoa = team_off.get('offense_dvoa', 0)
        pass_off_dvoa = team_off.get('passing_dvoa', 0)
        rush_off_dvoa = team_off.get('rushing_dvoa', 0)
        
        total_def_dvoa = opp_def.get('defense_dvoa', 0)
        pass_def_dvoa = opp_def.get('pass_defense_dvoa', 0)
        rush_def_dvoa = opp_def.get('rush_defense_dvoa', 0)
        
        # POSITION-SPECIFIC HANDLING
        if prop.position == 'QB':
            # QB: AGGRESSIVE SCORING for 80+ elite matchups
            if pass_off_dvoa >= 40:
                score += 30
                rationale.append(f"🔥🔥 ELITE O: {prop.team} +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa >= 20:
                score += 25
                rationale.append(f"💪 Elite passing O: {prop.team} +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa >= 10:
                score += 18
                rationale.append(f"💪 Strong passing O: {prop.team} +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa >= 5:
                score += 12
                rationale.append(f"Good passing O: +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa >= 0:
                score += 5
                rationale.append(f"Average passing O: +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa <= -10:
                score -= 15
                rationale.append(f"⚠️ Weak passing O: {pass_off_dvoa:.1f}%")
            
            if pass_def_dvoa >= 20:
                score += 25
                rationale.append(f"🎯 ELITE weak D: {prop.opponent} +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa >= 10:
                score += 18
                rationale.append(f"🎯 Weak pass D: {prop.opponent} +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa >= 3:
                score += 12
                rationale.append(f"Favorable pass D: +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa >= 0:
                score += 6
                rationale.append(f"Average pass D: +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa <= -10:
                score -= 15
                rationale.append(f"⚠️ ELITE PASS D: {pass_def_dvoa:.1f}%")
            
            # Stack bonus: Elite O vs weak D
            if pass_off_dvoa >= 20 and pass_def_dvoa >= 10:
                score += 15
                rationale.append("⚡ PREMIUM STACK: Elite O vs weak D")
            # REMOVED free +5 bonus - was causing OVER bias
        
        elif prop.position in ['WR', 'TE']:
            # WR/TE: AGGRESSIVE SCORING matching QB
            if pass_off_dvoa >= 40:
                score += 28
                rationale.append(f"🔥🔥 ELITE O: {prop.team} +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa >= 20:
                score += 23
                rationale.append(f"💪 Elite passing O: {prop.team} +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa >= 10:
                score += 16
                rationale.append(f"💪 Strong passing O: {prop.team} +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa >= 5:
                score += 11
                rationale.append(f"Good passing O: +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa >= 0:
                score += 4
                rationale.append(f"Average passing O: +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa <= -10:
                score -= 12
                rationale.append(f"⚠️ Weak passing O: {pass_off_dvoa:.1f}%")
            
            if pass_def_dvoa >= 20:
                score += 23
                rationale.append(f"🎯 ELITE weak D: {prop.opponent} +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa >= 10:
                score += 16
                rationale.append(f"🎯 Weak pass D: {prop.opponent} +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa >= 3:
                score += 11
                rationale.append(f"Favorable pass D: +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa >= 0:
                score += 5
                rationale.append(f"Average pass D: +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa <= -10:
                score -= 12
                rationale.append(f"⚠️ ELITE PASS D: {pass_def_dvoa:.1f}%")
            
            # Stack bonus
            if pass_off_dvoa >= 20 and pass_def_dvoa >= 10:
                score += 12
                rationale.append("⚡ PREMIUM STACK: Elite O vs weak D")
            # REMOVED free +3 bonus - was causing OVER bias
        
        elif prop.position == 'RB':
            if 'Rush' in prop.stat_type:
                if rush_off_dvoa >= 20:
                    score += 22
                    rationale.append(f"🔥 Elite rush O: +{rush_off_dvoa:.1f}%")
                elif rush_off_dvoa >= 10:
                    score += 16
                    rationale.append(f"💪 Strong rush O: +{rush_off_dvoa:.1f}%")
                elif rush_off_dvoa <= -10:
                    score -= 15
                    rationale.append(f"⚠️ Weak rush O: {rush_off_dvoa:.1f}%")
                
                if rush_def_dvoa >= 20:
                    score += 22
                    rationale.append(f"🎯 ELITE weak run D: {prop.opponent} +{rush_def_dvoa:.1f}%")
                elif rush_def_dvoa >= 10:
                    score += 16
                    rationale.append(f"🎯 Weak run D: {prop.opponent} +{rush_def_dvoa:.1f}%")
                elif rush_def_dvoa <= -10:
                    score -= 15
                    rationale.append(f"⚠️ Elite run D: {rush_def_dvoa:.1f}%")
                
                # Stack bonus
                if rush_off_dvoa >= 20 and rush_def_dvoa >= 10:
                    score += 12
                    rationale.append("⚡ PREMIUM STACK: Elite rush O vs weak D")
            
            elif 'Rec' in prop.stat_type:
                # RB receiving: Reduced scoring vs WR (RBs not priority targets)
                if pass_off_dvoa >= 20:
                    score += 10  # Reduced from 20
                    rationale.append(f"Good receiving O: +{pass_off_dvoa:.1f}%")
                elif pass_off_dvoa >= 10:
                    score += 7
                    rationale.append(f"Moderate receiving O: +{pass_off_dvoa:.1f}%")
                
                if pass_def_dvoa >= 20:
                    score += 9  # Reduced from 18
                    rationale.append(f"Weak pass D: +{pass_def_dvoa:.1f}%")
                elif pass_def_dvoa >= 10:
                    score += 6
                    rationale.append(f"Favorable pass D: +{pass_def_dvoa:.1f}%")
                
                if pass_off_dvoa >= 20 and pass_def_dvoa >= 10:
                    score += 5  # Reduced from 10
                    rationale.append("Modest receiving stack")
        
        direction = "OVER" if score >= 50 else "UNDER"
        
        if score >= 65:
            rationale.insert(0, f"✅ DVOA strongly favors {direction}")
        elif score <= 35:
            rationale.insert(0, f"⚠️ DVOA strongly favors {direction}")
        
        return (score, direction, rationale)
