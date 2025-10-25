"""
Parlay Builder - Builds up to 10 optimal parlays (3x 2/3/4 leg + 1x 5 leg) WITH POSITION DIVERSITY
Fixed to prevent QB-only bias by enforcing position diversity constraints
Enhanced to generate more parlays for better testing/calibration
"""

from typing import List, Dict, Set, Tuple, Optional
from .models import PropAnalysis, Parlay
import logging
import itertools

logger = logging.getLogger(__name__)

# Helper function to create a unique, hashable ID for a prop analysis
def get_prop_analysis_id(analysis: PropAnalysis) -> Tuple:
    prop = analysis.prop
    return (prop.player_name, prop.stat_type, prop.line, prop.team, prop.opponent)

class ParlayBuilder:
    """Builds optimal parlay combinations with position diversity"""

    def build_parlays(self, all_analyses: List[PropAnalysis],
                      min_confidence: int = 58) -> Dict[str, List[Parlay]]:
        """Main function to build up to 10 parlays with position diversity
        
        Distribution:
        - 3x 2-leg parlays
        - 3x 3-leg parlays
        - 3x 4-leg parlays
        - 1x 5-leg parlay
        """

        # Filter for props that meet the minimum betting confidence, sorted best first
        eligible_props = sorted(
            [prop for prop in all_analyses if prop.final_confidence >= min_confidence],
            key=lambda x: x.final_confidence,
            reverse=True
        )

        print(f"\n🎯 Building parlays from {len(eligible_props)} props (confidence {min_confidence}+)")
        print(f"   ✅ Enforcing position diversity to prevent QB-only bias...")
        print(f"   📊 Target: 10 parlays (3x 2-leg, 3x 3-leg, 3x 4-leg, 1x 5-leg)\n")

        # Set to track used prop IDs to prevent reuse across all parlays
        used_prop_ids: Set[Tuple] = set()

        parlays = {
            '2-leg': [],
            '3-leg': [],
            '4-leg': [],
            '5-leg': [],
        }

        # --- Build Three 2-LEG PARLAYS ---
        print("  📊 Building up to three 2-leg parlays...")
        parlays['2-leg'] = self.build_n_leg_parlays(2, 3, eligible_props, used_prop_ids)

        # --- Build Three 3-LEG PARLAYS ---
        print("\n  📊 Building up to three 3-leg parlays...")
        parlays['3-leg'] = self.build_n_leg_parlays(3, 3, eligible_props, used_prop_ids)

        # --- Build Three 4-LEG PARLAYS ---
        print("\n  📊 Building up to three 4-leg parlays...")
        parlays['4-leg'] = self.build_n_leg_parlays(4, 3, eligible_props, used_prop_ids)

        # --- Build One 5-LEG PARLAY ---
        print("\n  📊 Building up to one 5-leg parlay...")
        parlays['5-leg'] = self.build_n_leg_parlays(5, 1, eligible_props, used_prop_ids)

        total_2 = len(parlays['2-leg'])
        total_3 = len(parlays['3-leg'])
        total_4 = len(parlays['4-leg'])
        total_5 = len(parlays['5-leg'])
        total_all = total_2 + total_3 + total_4 + total_5
        
        logger.info(f"Built {total_2} 2-leg, {total_3} 3-leg, {total_4} 4-leg, {total_5} 5-leg parlays (Total: {total_all})")

        print(f"\n✅ Built {total_2} 2-leg, {total_3} 3-leg, {total_4} 4-leg, {total_5} 5-leg parlays")
        print(f"   📊 Total parlays: {total_all}/10")

        return parlays

    def build_n_leg_parlays(self, num_legs: int, max_parlays: int,
                            eligible_props: List[PropAnalysis],
                            used_prop_ids: Set[Tuple]) -> List[Parlay]:
        """ Tries to build 'max_parlays' parlays with 'num_legs' each, enforcing POSITION DIVERSITY. """
        built_parlays = []
        
        # Iterate to build up to max_parlays
        for i in range(max_parlays):
            current_legs = []
            players_in_current_parlay: Set[str] = set()
            positions_in_current_parlay: List[str] = []
            
            # Iterate through eligible props to find legs
            for prop_analysis in eligible_props:
                prop_id = get_prop_analysis_id(prop_analysis)
                player_name = prop_analysis.prop.player_name
                position = prop_analysis.prop.position
                
                # Check if prop already used globally or player used in this specific parlay
                if prop_id not in used_prop_ids and player_name not in players_in_current_parlay:
                    # =============== POSITION DIVERSITY CONSTRAINTS ===============
                    # These constraints prevent QB-only or same-position-heavy parlays
                    
                    position_counts = {}
                    for pos in positions_in_current_parlay:
                        position_counts[pos] = position_counts.get(pos, 0) + 1
                    
                    same_pos_count = position_counts.get(position, 0)
                    unique_positions = len(set(positions_in_current_parlay))
                    
                    # Enforce diversity constraints based on parlay leg count
                    can_add = True
                    if num_legs >= 5:
                        # For 5-leg: No more than 2 of same position (maximum diversity)
                        if same_pos_count >= 2:
                            can_add = False
                    elif num_legs == 4:
                        # For 4-leg: No more than 2 of same position (enforce variety)
                        if same_pos_count >= 2:
                            can_add = False
                    elif num_legs == 3:
                        # For 3-leg: No more than 2 of same position
                        if same_pos_count >= 2:
                            can_add = False
                    elif num_legs == 2:
                        # For 2-leg: Prefer different positions, but allow same if necessary
                        # Always allow first leg, encourage second to be different
                        pass  # Always try to add
                    
                    if can_add:
                        current_legs.append(prop_analysis)
                        players_in_current_parlay.add(player_name)
                        positions_in_current_parlay.append(position)
                        
                        # If we have enough legs, stop looking for this parlay
                        if len(current_legs) == num_legs:
                            break
            
            # If we successfully found enough unique legs
            if len(current_legs) == num_legs:
                # Mark these props as used globally
                for leg in current_legs:
                    used_prop_ids.add(get_prop_analysis_id(leg))
                
                # Determine risk and rationale
                unique_positions = set(leg.prop.position for leg in current_legs)
                is_same_game = len(set(f"{leg.prop.team}-{leg.prop.opponent}" for leg in current_legs)) == 1
                position_str = "/".join(sorted(unique_positions))
                
                risk = "MODERATE"
                rationale = f"✅ {position_str} stack ({num_legs} legs)"
                bonus = 0
                
                if is_same_game:
                    if num_legs == 2:
                        risk = "MODERATE"
                    elif num_legs <= 4:
                        risk = "HIGH"
                    else:  # 5-leg
                        risk = "VERY HIGH"
                    rationale = f"✅ Same-game {position_str} ({current_legs[0].prop.team} vs {current_legs[0].prop.opponent})"
                    bonus = 5 if num_legs <= 2 else (4 if num_legs == 3 else (3 if num_legs == 4 else 2))
                else:
                    # Bonus for game diversity
                    num_games = len(set(f"{leg.prop.team}-{leg.prop.opponent}" for leg in current_legs))
                    if num_games == num_legs:
                        rationale = f"✅ Diversified {position_str} across {num_games} games"
                        bonus = 4

                parlay = Parlay(
                    legs=current_legs,
                    parlay_type=f"{num_legs}-leg",
                    risk_level=risk,
                    rationale=rationale,
                    correlation_bonus=bonus
                )
                built_parlays.append(parlay)
                print(f"    ✅ Built {num_legs}-leg parlay #{i+1} (Conf: {parlay.combined_confidence}, Positions: {position_str})")

            else:
                # Could not find enough unique props for this parlay
                print(f"    ⚠️ Could not find enough unique props for {num_legs}-leg parlay #{i+1}")
                break

        return built_parlays


    def format_parlays_for_betting(self, parlays: Dict[str, List[Parlay]]) -> str:
        """Format the final parlays into a string card"""
        
        output = ["="*60, "🎯 ACTIONABLE PARLAY RECOMMENDATIONS", "="*60, ""]
        total_units = 0
        parlay_counter = {'2': 0, '3': 0, '4': 0, '5': 0}

        def format_single_parlay(parlay: Parlay, leg_count_str: str) -> List[str]:
            nonlocal total_units
            parlay_lines = []
            
            parlay_counter[leg_count_str] += 1
            parlay_num = parlay_counter[leg_count_str]

            parlay_lines.append(f"\n**PARLAY {leg_count_str}{parlay_num}** - {parlay.risk_level} RISK")
            parlay_lines.append(f"Combined Confidence: {parlay.combined_confidence} | EV: +{parlay.expected_value:.1f}%")
            
            units = parlay.recommended_units
            total_units += units
            parlay_lines.append(f"Recommended Bet: {units:.1f} units (${units*10:.0f} if $10/unit)")
            parlay_lines.append("")
            
            for j, leg in enumerate(parlay.legs, 1):
                parlay_lines.append(f"  Leg {j}: {leg.prop.player_name} ({leg.prop.team})")
                parlay_lines.append(f"         {leg.prop.stat_type} OVER {leg.prop.line}")
                parlay_lines.append(f"         vs {leg.prop.opponent} | Confidence: {leg.final_confidence}")
            
            parlay_lines.append("\n  Rationale:")
            parlay_lines.append(f"    • {parlay.rationale}")
            if parlay.correlation_bonus > 0:
                 parlay_lines.append(f"    • Correlation bonus: +{parlay.correlation_bonus} confidence")
            
            top_reasons = set()
            for leg in parlay.legs:
                if leg.rationale:
                     # Add only the first rationale point if available
                     top_reasons.add(leg.rationale[0].strip())
            
            for reason in list(top_reasons)[:3]: # Show top 3 unique reasons
                parlay_lines.append(f"    • {reason}")
            return parlay_lines

        # --- Format Each Leg Count ---
        for leg_count, leg_str in [(2, '2'), (3, '3'), (4, '4'), (5, '5')]:
            parlay_list = parlays.get(f'{leg_count}-leg', [])
            if not parlay_list:
                continue
                
            output.append("\n" + "="*60)
            output.append(f"📊 {leg_count}-LEG PARLAYS")
            output.append("="*60)
            
            for parlay in parlay_list:
                output.extend(format_single_parlay(parlay, leg_str))

        # --- TIPS ---
        output.append("\n" + "="*60)
        output.append("💡 BETTING TIPS")
        output.append("="*60)
        output.append("• 2-leg parlays have highest hit rate but lower payout")
        output.append("• 3-leg and 4-leg balance risk/reward")
        output.append("• 5-leg is high risk/high reward - consider reducing units")
        output.append("• Same-game parlays have correlation bonus but higher variance")
        output.append("• Uncorrelated parlays (different games) are safer")
        output.append("• Position diversity reduces correlation risk")
        output.append("• Never bet more than you can afford to lose!")
        
        # Total summary
        output.append("\n" + "="*60)
        output.append("📊 SUMMARY")
        output.append("="*60)
        output.append(f"Total Parlays: {sum(len(p) for p in parlays.values())}/10")
        output.append(f"Total Units: {total_units:.1f}")
        output.append(f"At $10/unit: ${total_units*10:.0f}")
        output.append("="*60)
        
        return "\n".join(output)
