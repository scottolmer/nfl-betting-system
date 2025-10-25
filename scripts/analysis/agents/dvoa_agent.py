"""
DVOA Agent - Analyzes team efficiency
"""

from typing import Dict, List, Tuple
from .base_agent import BaseAgent


class DVOAAgent(BaseAgent):
    """Analyzes matchups using DVOA"""
    
    def __init__(self):
        super().__init__(weight=2.0)
    
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
        
        total_off_dvoa = team_off.get('offense_weighted_dvoa', 
                                      team_off.get('offense_dvoa', 0))
        pass_off_dvoa = team_off.get('passing_dvoa', 0)
        rush_off_dvoa = team_off.get('rushing_dvoa', 0)
        
        total_def_dvoa = opp_def.get('defense_weighted_dvoa',
                                     opp_def.get('defense_dvoa', 0))
        pass_def_dvoa = opp_def.get('pass_defense_dvoa', 0)
        rush_def_dvoa = opp_def.get('rush_defense_dvoa', 0)
        
        if prop.position in ['QB', 'WR', 'TE']:
            if pass_off_dvoa >= 10:
                score += 12  # REDUCED from 20 to prevent QB bias
                rationale.append(f"💪 Elite passing O: {prop.team} +{pass_off_dvoa:.1f}% Pass DVOA")
            elif pass_off_dvoa >= 5:
                score += 7  # REDUCED from 12
                rationale.append(f"Strong passing O: +{pass_off_dvoa:.1f}% Pass DVOA")
            elif pass_off_dvoa >= 0:
                score += 2  # REDUCED from 5
                rationale.append(f"Average passing O: +{pass_off_dvoa:.1f}% Pass DVOA")
            elif pass_off_dvoa <= -10:
                score -= 10
                rationale.append(f"⚠️ Weak passing O: {pass_off_dvoa:.1f}% Pass DVOA")
            
            if pass_def_dvoa >= 10:
                score += 14  # REDUCED from 22
                rationale.append(f"🎯 WEAK PASS D: {prop.opponent} +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa >= 3:
                score += 9  # REDUCED from 14
                rationale.append(f"Favorable pass D: +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa >= 0:
                score += 3  # REDUCED from 6
                rationale.append(f"Average pass D: +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa <= -10:
                score -= 14  # REDUCED from 18
                rationale.append(f"⚠️ ELITE PASS D: {pass_def_dvoa:.1f}%")
            
            if pass_off_dvoa >= 10 and pass_def_dvoa >= 5:
                score += 8  # REDUCED from 15
                rationale.append("🔥 PREMIUM MATCHUP: Elite passing O vs weak pass D")
        
        elif prop.position == 'RB':
            if 'Rush' in prop.stat_type:
                if rush_off_dvoa >= 10:
                    score += 12
                    rationale.append(f"Strong rush O: +{rush_off_dvoa:.1f}% Rush DVOA")
                elif rush_off_dvoa <= -10:
                    score -= 10
                    rationale.append(f"⚠️ Weak rush O: {rush_off_dvoa:.1f}% Rush DVOA")
                
                if rush_def_dvoa >= 10:
                    score += 15
                    rationale.append(f"🎯 WEAK RUN D: {prop.opponent} +{rush_def_dvoa:.1f}%")
                elif rush_def_dvoa <= -10:
                    score -= 12
                    rationale.append(f"⚠️ Elite run D: {rush_def_dvoa:.1f}%")
            
            elif 'Rec' in prop.stat_type:
                if pass_off_dvoa >= 10:
                    score += 10
                    rationale.append(f"Pass-catching RB benefits: +{pass_off_dvoa:.1f}% Pass DVOA")
                if pass_def_dvoa >= 10:
                    score += 8
                    rationale.append(f"Favorable for RB receiving: +{pass_def_dvoa:.1f}% pass D")
        
        direction = "OVER" if score >= 50 else "UNDER"
        
        if score >= 65:
            rationale.insert(0, f"✅ DVOA strongly favors {direction}")
        elif score <= 35:
            rationale.insert(0, f"⚠️ DVOA strongly favors {direction}")
        
        return (score, direction, rationale)
