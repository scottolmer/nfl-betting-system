"""
DVOA Agent - Analyzes team efficiency
UPDATED: QB-friendly scoring with fair WR/TE competition
UPDATED: Incorporates individual QB EPA/DVOA analytics
"""

from typing import Dict, List, Tuple
import re
from .base_agent import BaseAgent


def normalize_player_name(name: str) -> str:
    """Normalize player name for matching"""
    if not name:
        return name
    name = name.replace('.', '')
    name = re.sub(r'\s+', ' ', name)
    return name.strip().lower()


class DVOAAgent(BaseAgent):
    """Analyzes matchups using DVOA"""

    def __init__(self, weight: float = 2.0):
        super().__init__(weight=weight)

    def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
        rationale = []
        score = 50

        off_dvoa = context.get('dvoa_offensive', {})
        def_dvoa = context.get('dvoa_defensive', {})
        qb_analytics = context.get('qb_analytics', {})
        
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
            # First check individual QB analytics (EPA, DVOA per QB)
            qb_name = normalize_player_name(prop.player_name)
            qb_data = qb_analytics.get(qb_name, {})

            if qb_data:
                # Individual QB efficiency metrics
                qb_epa = qb_data.get('epa_per_dropback', 0)
                qb_dvoa = qb_data.get('dvoa', 0)
                qb_rating = qb_data.get('passer_rating', 0)
                qb_ypa = qb_data.get('yards_per_attempt', 0)

                # EPA per dropback analysis (excellent predictor)
                if qb_epa >= 0.25:
                    score += 15
                    rationale.append(f"🔥 Elite EPA/dropback: {qb_epa:.3f}")
                elif qb_epa >= 0.10:
                    score += 10
                    rationale.append(f"💪 Strong EPA/dropback: {qb_epa:.3f}")
                elif qb_epa >= 0:
                    score += 5
                    rationale.append(f"Positive EPA: {qb_epa:.3f}")
                elif qb_epa <= -0.10:
                    score -= 12
                    rationale.append(f"⚠️ Negative EPA: {qb_epa:.3f}")

                # Individual QB DVOA
                if qb_dvoa >= 30:
                    score += 12
                    rationale.append(f"🔥 Elite QB DVOA: {qb_dvoa:.1f}%")
                elif qb_dvoa >= 15:
                    score += 8
                    rationale.append(f"Strong QB DVOA: {qb_dvoa:.1f}%")
                elif qb_dvoa <= -15:
                    score -= 10
                    rationale.append(f"⚠️ Poor QB DVOA: {qb_dvoa:.1f}%")

                # Yards per attempt (volume indicator)
                if qb_ypa >= 8.5:
                    score += 6
                    rationale.append(f"High YPA: {qb_ypa:.1f}")
                elif qb_ypa <= 6.0:
                    score -= 6
                    rationale.append(f"Low YPA: {qb_ypa:.1f}")

            # Team-level DVOA (still valuable)
            if pass_off_dvoa >= 40:
                score += 20  # Reduced since we have individual QB data now
                rationale.append(f"🔥 ELITE team O: {prop.team} +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa >= 20:
                score += 15
                rationale.append(f"💪 Elite passing O: {prop.team} +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa >= 10:
                score += 10
                rationale.append(f"💪 Strong passing O: {prop.team} +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa >= 5:
                score += 6
                rationale.append(f"Good passing O: +{pass_off_dvoa:.1f}%")
            elif pass_off_dvoa <= -10:
                score -= 10
                rationale.append(f"⚠️ Weak passing O: {pass_off_dvoa:.1f}%")

            # Opponent pass defense
            if pass_def_dvoa >= 20:
                score += 18
                rationale.append(f"🎯 ELITE weak D: {prop.opponent} +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa >= 10:
                score += 12
                rationale.append(f"🎯 Weak pass D: {prop.opponent} +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa >= 3:
                score += 8
                rationale.append(f"Favorable pass D: +{pass_def_dvoa:.1f}%")
            elif pass_def_dvoa <= -10:
                score -= 12
                rationale.append(f"⚠️ ELITE PASS D: {pass_def_dvoa:.1f}%")

            # Stack bonus: Elite O vs weak D
            if pass_off_dvoa >= 20 and pass_def_dvoa >= 10:
                score += 10
                rationale.append("⚡ PREMIUM STACK: Elite O vs weak D")
        
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
