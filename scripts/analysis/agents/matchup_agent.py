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

    def __init__(self, weight: float = 1.8):
        super().__init__(weight=weight)
    
    def analyze(self, prop, context: Dict) -> Tuple[float, str, List[str]]:
        rationale = []
        score = 50
        
        # This key ('defensive_vs_receiver') is now created by our new function in run_analysis.py
        def_vs_receiver = context.get('defensive_vs_receiver', {})
        opp_def = def_vs_receiver.get(prop.opponent, {})
        
        if not opp_def:
            rationale.append(f"⚠️ Position-specific defensive data unavailable for {prop.opponent}")
            return (50, "AVOID", rationale)
        
        # Handle QB separately
        if prop.position == 'QB':
            def_dvoa = context.get('dvoa_defensive', {}).get(prop.opponent, {})
            pass_def_dvoa = def_dvoa.get('pass_defense_dvoa', 0)
            
            if pass_def_dvoa >= 20:
                score += 25
                rationale.append(f"🔥 Weak pass defense: {prop.opponent} allows +{pass_def_dvoa:.1f}% DVOA")
            elif pass_def_dvoa >= 5:
                score += 15
                rationale.append(f"🎯 Favorable pass matchup: +{pass_def_dvoa:.1f}% DVOA")
            elif pass_def_dvoa >= -10:
                rationale.append(f"⚖️ Neutral pass matchup: {pass_def_dvoa:.1f}% DVOA")
            elif pass_def_dvoa >= -25:
                score -= 12
                rationale.append(f"⚠️ Strong pass defense: {pass_def_dvoa:.1f}% DVOA")
            else:
                score -= 20
                rationale.append(f"🛡️ Elite pass defense: {pass_def_dvoa:.1f}% DVOA")
            
            direction = "OVER" if score >= 50 else "UNDER"
            return (score, direction, rationale)
        
        wr_role = self._classify_wr_role(prop.player_name, prop.position, context)
        align_info = self._get_alignment_efficiency(prop.player_name, context)

        if wr_role in ['WR1', 'WR2', 'WR3']:
            # Use the keys we mapped in our new transformer
            dvoa_key = f'vs_{wr_role.lower()}_dvoa'
            dvoa = opp_def.get(dvoa_key, 0)

            # Add alignment context to rationale
            if align_info['slot_pct'] >= 60:
                rationale.append(f"📍 Slot receiver ({align_info['slot_pct']:.0f}% slot routes)")
            elif align_info['wide_pct'] >= 70:
                rationale.append(f"📍 Outside receiver ({align_info['wide_pct']:.0f}% wide routes)")

            # Check yards per route efficiency
            if align_info['slot_pct'] >= 50 and align_info['slot_ypr'] >= 2.0:
                score += 5
                rationale.append(f"Efficient from slot: {align_info['slot_ypr']:.1f} yds/route")
            elif align_info['wide_pct'] >= 50 and align_info['wide_ypr'] >= 2.5:
                score += 5
                rationale.append(f"Efficient from outside: {align_info['wide_ypr']:.1f} yds/route")

            # DVOA-based scoring
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
            if 'Rush' in prop.stat_type or 'Rushing' in prop.stat_type:
                # RUSHING: Use rush_defense_dvoa (primary driver for rushing volume)
                def_dvoa = context.get('dvoa_defensive', {}).get(prop.opponent, {})
                rush_def_dvoa = def_dvoa.get('rush_defense_dvoa', 0)
                
                if rush_def_dvoa >= 25:
                    score += 25
                    rationale.append(f"🔥🔥 ELITE weak run D: {prop.opponent} allows +{rush_def_dvoa:.1f}% DVOA")
                elif rush_def_dvoa >= 15:
                    score += 20
                    rationale.append(f"🔥 Great weak run D: +{rush_def_dvoa:.1f}% DVOA")
                elif rush_def_dvoa >= 5:
                    score += 12
                    rationale.append(f"🎯 Favorable run matchup: +{rush_def_dvoa:.1f}% DVOA")
                elif rush_def_dvoa >= -5:
                    rationale.append(f"⚖️ Neutral run matchup: {rush_def_dvoa:.1f}% DVOA")
                elif rush_def_dvoa >= -15:
                    score -= 12
                    rationale.append(f"⚠️ Strong run defense: {rush_def_dvoa:.1f}% DVOA")
                elif rush_def_dvoa >= -25:
                    score -= 18
                    rationale.append(f"⚠️⚠️ ELITE run D: {rush_def_dvoa:.1f}% DVOA")
                else:
                    score -= 25
                    rationale.append(f"🛡️ ELITE ELITE run D: {rush_def_dvoa:.1f}% DVOA")
            
            elif 'Rec' in prop.stat_type:
                # RECEIVING: Use vs_rb_dvoa (receiving-specific)
                rb_dvoa = opp_def.get('vs_rb_dvoa', 0)
                
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
        """Classify WR role using NORMALIZED names and alignment data"""
        if position == 'TE':
            return 'TE'
        if position == 'RB':
            return 'RB'
        if position == 'QB':
            return 'QB'

        # Normalize the player name
        normalized_name = normalize_player_name(player_name).lower()

        usage = context.get('usage', {})
        alignment = context.get('alignment', {})

        # Try normalized name first, then original
        player_usage = usage.get(normalized_name, usage.get(player_name.lower(), {}))
        player_alignment = alignment.get(normalized_name, alignment.get(player_name.lower(), {}))

        target_share = player_usage.get('target_share_pct', 0)
        slot_pct = player_alignment.get('slot_pct', 0)
        wide_pct = player_alignment.get('wide_pct', 0)

        # Primary classification based on alignment + target share
        if slot_pct >= 60:
            # Primarily slot receiver -> WR3 matchup (slot coverage)
            return 'WR3'
        elif wide_pct >= 70 and target_share >= 22:
            # Outside receiver with high target share -> WR1
            return 'WR1'
        elif wide_pct >= 50 and target_share >= 15:
            # Outside receiver with moderate targets -> WR2
            return 'WR2'
        elif target_share >= 22:
            # High target share regardless of alignment -> WR1
            return 'WR1'
        elif target_share >= 15:
            return 'WR2'

        return 'WR3'

    def _get_alignment_efficiency(self, player_name: str, context: Dict) -> dict:
        """Get alignment-specific efficiency metrics for a receiver"""
        normalized_name = normalize_player_name(player_name).lower()
        alignment = context.get('alignment', {})
        player_align = alignment.get(normalized_name, alignment.get(player_name.lower(), {}))

        return {
            'slot_pct': player_align.get('slot_pct', 0),
            'wide_pct': player_align.get('wide_pct', 0),
            'primary_alignment': player_align.get('primary_alignment', 'UNKNOWN'),
            'slot_ypr': player_align.get('slot_yards_per_route', 0),
            'wide_ypr': player_align.get('wide_yards_per_route', 0),
        }
