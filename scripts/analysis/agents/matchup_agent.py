"""
Matchup Agent - Position-Specific Defensive Analysis (COMPLETE DVOA RANGES)
"""

from typing import Dict, List, Tuple
from .base_agent import BaseAgent
import re


def normalize_player_name(name: str) -> str:
    """Normalize player name for matching"""
    if not name:
        return name
    name = name.replace('.', '')
    name = re.sub(r'\s+', ' ', name)
    return name.strip()


class MatchupAgent(BaseAgent):
    """Analyzes defensive matchups with position-specific DVOA"""
    
    def __init__(self):
        super().__init__(weight=1.8)
    
    def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
        rationale = []
        score = 50
        
        # This key ('defensive_vs_receiver') is now created by our new function in run_analysis.py
        def_vs_receiver = context.get('defensive_vs_receiver', {})
        opp_def = def_vs_receiver.get(prop.opponent, {})
        
        if not opp_def:
            rationale.append(f"⚠️ Position-specific defensive data unavailable for {prop.opponent}")
            return (50, "AVOID", rationale)
        
        wr_role = self._classify_wr_role(prop.player_name, prop.position, context)
        
        if wr_role in ['WR1', 'WR2', 'WR3']:
            # Use the keys we mapped in our new transformer
            dvoa_key = f'vs_{wr_role.lower()}_dvoa'
            dvoa = opp_def.get(dvoa_key, 0)
            
            # Simplified logic (removed yds_allowed)
            if dvoa >= 50:
                score += 25
                rationale.append(
                    f"🔥🔥 PREMIUM {wr_role} MATCHUP: {prop.opponent} allows "
                    f"+{dvoa:.1f}% DVOA vs {wr_role}"
                )
            elif dvoa >= 30:
                score += 20
                rationale.append(f"🔥 ELITE {wr_role} MATCHUP: +{dvoa:.1f}% DVOA")
            elif dvoa >= 15:
                score += 12
                rationale.append(f"🎯 Great {wr_role} matchup: +{dvoa:.1f}% DVOA")
            elif dvoa >= 5:
                score += 5
                rationale.append(f"✓ Favorable {wr_role} matchup: +{dvoa:.1f}% DVOA")
            elif dvoa >= -15:
                rationale.append(f"⚖️ Neutral {wr_role} matchup: {dvoa:.1f}% DVOA")
            elif dvoa >= -30:
                score -= 10
                rationale.append(f"⚠️ Tough {wr_role} matchup: {dvoa:.1f}% DVOA")
            else:  # dvoa < -30
                score -= 20
                rationale.append(f"⚠️⚠️ ELITE {wr_role} COVERAGE: {dvoa:.1f}% DVOA")
        
        elif prop.position == 'TE':
            te_dvoa = opp_def.get('vs_te_dvoa', 0)
            
            # Simplified logic (removed te_yds)
            if te_dvoa >= 50:
                score += 25
                rationale.append(f"🔥🔥 ELITE TE MATCHUP: +{te_dvoa:.1f}% DVOA")
            elif te_dvoa >= 30:
                score += 20
                rationale.append(f"🔥 Great TE matchup: +{te_dvoa:.1f}% DVOA")
            elif te_dvoa >= 15:
                score += 12
                rationale.append(f"🎯 Favorable TE matchup: +{te_dvoa:.1f}% DVOA")
            elif te_dvoa >= -15:
                rationale.append(f"⚖️ Neutral TE matchup: {te_dvoa:.1f}% DVOA")
            elif te_dvoa >= -30:
                score -= 10
                rationale.append(f"⚠️ Tough TE matchup: {te_dvoa:.1f}% DVOA")
            else:
                score -= 20
                rationale.append(f"⚠️ Elite TE coverage: {te_dvoa:.1f}% DVOA")
        
        elif prop.position == 'RB':
            rb_dvoa = opp_def.get('vs_rb_dvoa', 0)
            
            if 'Rec' in prop.stat_type:
                if rb_dvoa >= 40:
                    score += 20
                    rationale.append(f"🔥 Weak vs RB receiving: +{rb_dvoa:.1f}% DVOA")
                elif rb_dvoa >= 15:
                    score += 10
                    rationale.append(f"✓ Favorable RB receiving: +{rb_dvoa:.1f}% DVOA")
                elif rb_dvoa >= -15:
                    rationale.append(f"⚖️ Neutral RB receiving: {rb_dvoa:.1f}% DVOA")
                elif rb_dvoa <= -30:
                    score -= 15
                    rationale.append(f"⚠️ Strong vs RB receiving: {rb_dvoa:.1f}% DVOA")
        
        direction = "OVER" if score >= 50 else "UNDER"
        
        if score != 50:
            rationale.insert(0, f"✅ Position matchup {('favors' if score > 50 else 'disfavors')} {direction}")
        
        return (score, direction, rationale)
    
    def _classify_wr_role(self, player_name: str, position: str, context: Dict) -> str:
        """Classify WR role using NORMALIZED names"""
        if position == 'TE':
            return 'TE'
        if position == 'RB':
            return 'RB'
        if position == 'QB':
            return 'QB'
        
        # Normalize the player name
        normalized_name = normalize_player_name(player_name)
        
        usage = context.get('usage', {})
        alignment = context.get('alignment', {})
        
        # Try normalized name first, then original
        player_usage = usage.get(normalized_name, usage.get(player_name, {}))
        player_alignment = alignment.get(normalized_name, alignment.get(player_name, {}))
        
        target_share = player_usage.get('target_share_pct', 0)
        slot_pct = player_alignment.get('slot_pct', 0)
        
        # WR1: High target share + plays outside (not slot)
        if target_share >= 22 and slot_pct < 40:
            return 'WR1'
        # Slot WR = WR3
        if slot_pct >= 60:
            return 'WR3'
        # WR2: Moderate target share
        if target_share >= 15:
            return 'WR2'
        return 'WR3'
