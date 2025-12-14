"""
Parlay Rebuilder - Reconstructs parlays using validated props
Takes props from rejected parlays and rebuilds new parlays with valid props
"""

from typing import List, Dict, Set, Tuple
from collections import defaultdict
import logging
from .models import Parlay, PropAnalysis
from .prop_availability_validator import PropAvailabilityValidator

logger = logging.getLogger(__name__)


class ParlayRebuilder:
    """
    Rebuilds parlays using only validated, available props

    Key features:
    1. Extracts valid props from rejected parlays
    2. Combines with other available props
    3. Rebuilds optimized parlays respecting platform constraints
    4. Maintains diversity (player usage limits)
    """

    def __init__(self, db_path: str = "bets.db"):
        self.validator = PropAvailabilityValidator(db_path)

    def rebuild_parlays(self,
                       valid_props_pool: List[PropAnalysis],
                       additional_props: List[PropAnalysis],
                       target_counts: Dict[str, int] = None,
                       min_confidence: int = 58) -> Dict[str, List[Parlay]]:
        """
        Rebuild parlays from scratch using validated props

        Args:
            valid_props_pool: Props extracted from validated parlays
            additional_props: Other available props to fill parlays
            target_counts: Target number of parlays per leg count (e.g., {"2-leg": 3, "3-leg": 3})
            min_confidence: Minimum confidence threshold

        Returns:
            Dict of parlay_type -> List[Parlay]
        """
        if target_counts is None:
            target_counts = {
                "2-leg": 3,
                "3-leg": 3,
                "4-leg": 3,
                "5-leg": 1
            }

        # Combine all props and filter
        all_props = valid_props_pool + additional_props

        # Remove duplicates based on prop signature
        seen_signatures = set()
        unique_props = []
        for prop in all_props:
            signature = self._get_prop_signature(prop)
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_props.append(prop)

        # Filter by confidence
        eligible_props = [p for p in unique_props if p.final_confidence >= min_confidence]

        # Filter by availability (remove known unavailable props)
        eligible_props = self.validator.filter_available_props(eligible_props)

        # Filter by minimum thresholds (remove props with lines too small for DraftKings)
        eligible_props = self.validator.filter_by_minimum_thresholds(eligible_props, verbose=True)

        # Sort by confidence
        eligible_props.sort(key=lambda x: x.final_confidence, reverse=True)

        print(f"\n🔨 REBUILDING PARLAYS")
        print(f"   📦 Total unique props: {len(unique_props)}")
        print(f"   ✅ Eligible props (conf {min_confidence}+): {len(eligible_props)}")
        print(f"   🎯 Target parlays: {sum(target_counts.values())}\n")

        # Build parlays
        parlays = {
            '2-leg': [],
            '3-leg': [],
            '4-leg': [],
            '5-leg': [],
        }

        used_prop_signatures: Set[str] = set()
        player_usage_count: Dict[str, int] = defaultdict(int)
        all_used_players: Set[str] = set()

        for leg_count_str, target_count in target_counts.items():
            leg_count = int(leg_count_str.split('-')[0])

            print(f"  🔨 Building {target_count}x {leg_count_str} parlays...")

            parlays[leg_count_str] = self._build_n_leg_parlays(
                num_legs=leg_count,
                max_parlays=target_count,
                eligible_props=eligible_props,
                used_prop_signatures=used_prop_signatures,
                player_usage_count=player_usage_count,
                all_used_players=all_used_players,
                max_player_uses=3
            )

        # Summary
        total = sum(len(p) for p in parlays.values())
        print(f"\n✅ Rebuilt {total} parlays using validated props")
        print(f"   📊 Unique players used: {len(player_usage_count)}")

        return parlays

    def _build_n_leg_parlays(self,
                            num_legs: int,
                            max_parlays: int,
                            eligible_props: List[PropAnalysis],
                            used_prop_signatures: Set[str],
                            player_usage_count: Dict[str, int],
                            all_used_players: Set[str],
                            max_player_uses: int = 3) -> List[Parlay]:
        """Build N-leg parlays with player diversity"""
        built_parlays = []

        for i in range(max_parlays):
            # Sort props: prioritize unused players, then by confidence
            def prop_sort_key(prop):
                player_name = prop.prop.player_name
                already_used = 1 if player_name in all_used_players else 0
                confidence = -prop.final_confidence
                return (already_used, confidence)

            sorted_props = sorted(eligible_props, key=prop_sort_key)

            current_legs = []
            players_in_current_parlay: Set[str] = set()

            for prop_analysis in sorted_props:
                prop_signature = self._get_prop_signature(prop_analysis)
                player_name = prop_analysis.prop.player_name

                if (prop_signature not in used_prop_signatures and
                    player_usage_count.get(player_name, 0) < max_player_uses and
                    player_name not in players_in_current_parlay):

                    current_legs.append(prop_analysis)
                    players_in_current_parlay.add(player_name)

                    if len(current_legs) == num_legs:
                        break

            if len(current_legs) == num_legs:
                # Validate this combination doesn't violate rules
                is_valid, violations = self.validator.validate_parlay_props(current_legs)

                if not is_valid:
                    print(f"    ⚠️  Parlay #{i+1} skipped - rule violations: {violations[0]}")
                    continue

                # Mark props and players as used
                for leg in current_legs:
                    used_prop_signatures.add(self._get_prop_signature(leg))
                    player_name = leg.prop.player_name
                    player_usage_count[player_name] = player_usage_count.get(player_name, 0) + 1
                    all_used_players.add(player_name)

                # Create parlay
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
                    else:
                        risk = "VERY HIGH"
                    rationale = f"✅ Same-game {position_str} ({current_legs[0].prop.team} vs {current_legs[0].prop.opponent})"
                    bonus = 5 if num_legs <= 2 else (4 if num_legs == 3 else (3 if num_legs == 4 else 2))
                else:
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
                print(f"    ✅ Built {num_legs}-leg parlay #{i+1} (Conf: {parlay.combined_confidence})")
            else:
                print(f"    ⚠️  Could not find enough unique props for {num_legs}-leg parlay #{i+1}")

        return built_parlays

    def _get_prop_signature(self, prop: PropAnalysis) -> str:
        """Generate unique signature for a prop"""
        p = prop.prop
        return f"{p.player_name}|{p.stat_type}|{p.bet_type}|{p.line}|{p.team}|{p.opponent}"

    def extract_valid_props_from_rejected_parlays(self,
                                                  rejected_parlays: List[Dict]) -> List[PropAnalysis]:
        """
        Extract props marked as valid from rejected parlays

        Args:
            rejected_parlays: List of parlay validation dicts with "parlay" and "reason" keys

        Returns:
            List of valid PropAnalysis objects
        """
        valid_props = []

        for validation in rejected_parlays:
            parlay = validation["parlay"]
            reason = validation.get("reason", "")

            # If reason indicates which props were invalid, extract the valid ones
            # For now, we rely on the prop_availability table marked during interactive validation
            for leg in parlay.legs:
                # Check if this prop was marked as available
                if self._is_prop_available(leg.prop):
                    valid_props.append(leg)

        return valid_props

    def _is_prop_available(self, prop) -> bool:
        """Check if a prop is marked as available in the database"""
        import sqlite3

        conn = sqlite3.connect(self.validator.db_path)
        cursor = conn.cursor()

        prop_signature = f"{prop.player_name}|{prop.stat_type}|{prop.bet_type}|{prop.line}"

        cursor.execute("""
            SELECT is_available FROM prop_availability
            WHERE prop_signature = ?
        """, (prop_signature,))

        result = cursor.fetchone()
        conn.close()

        if result is None:
            return True  # Unknown = assume available
        return result[0] == 1
