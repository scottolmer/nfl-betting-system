"""
Interactive Parlay Validation Interface
Allows manual validation of parlays and props, learning which ones work on DraftKings Pick6
"""

from typing import List, Dict, Tuple
import sqlite3
import json
from datetime import datetime
from .models import Parlay, PropAnalysis
from .prop_availability_validator import PropAvailabilityValidator


class ParlayValidatorInterface:
    """
    Interactive interface for validating parlays and rebuilding with valid props

    Workflow:
    1. Display generated parlays
    2. User marks props as valid/invalid
    3. System learns from feedback
    4. Rebuilds parlays using only valid props
    """

    def __init__(self, db_path: str = "bets.db"):
        self.db_path = db_path
        self.validator = PropAvailabilityValidator(db_path)

    def validate_parlays_interactive(self, parlays: Dict[str, List[Parlay]]) -> Dict:
        """
        Interactive validation workflow for parlays

        Returns:
            Dict with validation results and valid props pool
        """
        print("\n" + "="*80)
        print("🔍 PARLAY VALIDATION - DraftKings Pick6 Availability Check")
        print("="*80)
        print("\nThis will help identify which props are actually available on the platform.")
        print("You'll review each parlay and mark props as VALID or INVALID.\n")

        all_props = []
        parlay_validations = []

        # Flatten all parlays to get all props
        for parlay_type, parlay_list in parlays.items():
            for parlay in parlay_list:
                all_props.extend(parlay.legs)

        # Check each parlay against rules first
        print("📋 Pre-filtering with validation rules...\n")
        for parlay_type, parlay_list in parlays.items():
            for i, parlay in enumerate(parlay_list, 1):
                is_valid, violations = self.validator.validate_parlay_props(parlay.legs)

                if not is_valid:
                    print(f"❌ {parlay_type.upper()} Parlay #{i} - RULE VIOLATIONS:")
                    for violation in violations:
                        print(f"   {violation}")

                    parlay_validations.append({
                        "parlay": parlay,
                        "parlay_type": parlay_type,
                        "is_valid": False,
                        "reason": "Rule violations: " + "; ".join(violations)
                    })
                else:
                    print(f"✅ {parlay_type.upper()} Parlay #{i} - Passed rule checks")
                    parlay_validations.append({
                        "parlay": parlay,
                        "parlay_type": parlay_type,
                        "is_valid": True,
                        "reason": None
                    })

        # Now interactive review
        print("\n" + "="*80)
        print("🎯 INTERACTIVE VALIDATION")
        print("="*80)
        print("\nReview parlays that passed rule checks:")
        print("For each parlay, you can:")
        print("  • ACCEPT (A) - All props are available on DraftKings Pick6")
        print("  • REJECT (R) - One or more props aren't available")
        print("  • SKIP (S) - Skip this parlay for now\n")

        valid_parlays = []
        invalid_parlays = []
        all_valid_props_pool = []

        for validation in parlay_validations:
            if not validation["is_valid"]:
                # Already rejected by rules
                invalid_parlays.append(validation)
                continue

            parlay = validation["parlay"]
            parlay_type = validation["parlay_type"]

            print("\n" + "-"*80)
            print(f"📊 {parlay_type.upper()} (Confidence: {parlay.combined_confidence})")
            print("-"*80)

            for j, leg in enumerate(parlay.legs, 1):
                print(f"  {j}. {leg.prop.player_name} ({leg.prop.team}) - {leg.prop.stat_type} {leg.prop.bet_type} {leg.prop.line}")
                print(f"     Confidence: {leg.final_confidence} | vs {leg.prop.opponent}")

            print("\n  " + parlay.rationale)

            # Get user input
            while True:
                response = input("\n  👉 Accept/Reject/Skip? (A/R/S): ").strip().upper()

                if response == 'A':
                    # Mark all props as valid
                    for leg in parlay.legs:
                        self.validator.mark_prop_available(leg.prop, True, "Validated in parlay")
                        all_valid_props_pool.append(leg)

                    valid_parlays.append(validation)
                    print("  ✅ Parlay accepted - all props marked as available")
                    break

                elif response == 'R':
                    # Ask which props are invalid
                    print("\n  Which props are NOT available? (comma-separated numbers, e.g., '1,3'):")
                    invalid_nums = input("  👉 Invalid props: ").strip()

                    try:
                        invalid_indices = [int(n.strip()) - 1 for n in invalid_nums.split(',') if n.strip()]

                        # Mark invalid props
                        for idx in invalid_indices:
                            if 0 <= idx < len(parlay.legs):
                                leg = parlay.legs[idx]
                                self.validator.mark_prop_available(leg.prop, False, "Unavailable on DK Pick6")
                                print(f"  ❌ Marked as unavailable: {leg.prop.player_name} {leg.prop.stat_type} {leg.prop.bet_type}")

                        # Mark valid props (the ones not rejected)
                        for idx, leg in enumerate(parlay.legs):
                            if idx not in invalid_indices:
                                self.validator.mark_prop_available(leg.prop, True, "Available on DK Pick6")
                                all_valid_props_pool.append(leg)

                        validation["is_valid"] = False
                        validation["reason"] = f"Props {invalid_nums} unavailable"
                        invalid_parlays.append(validation)
                        print("  ❌ Parlay rejected - props marked accordingly")
                        break

                    except ValueError:
                        print("  ⚠️  Invalid input. Please enter comma-separated numbers.")
                        continue

                elif response == 'S':
                    print("  ⏭️  Skipped")
                    break

                else:
                    print("  ⚠️  Invalid choice. Please enter A, R, or S.")

        print("\n" + "="*80)
        print("📊 VALIDATION SUMMARY")
        print("="*80)
        print(f"✅ Valid parlays: {len(valid_parlays)}")
        print(f"❌ Invalid parlays: {len(invalid_parlays)}")
        print(f"📦 Valid props pool: {len(all_valid_props_pool)} props")

        # Save validation session
        self._save_validation_session(valid_parlays, invalid_parlays)

        return {
            "valid_parlays": valid_parlays,
            "invalid_parlays": invalid_parlays,
            "valid_props_pool": all_valid_props_pool,
            "stats": self.validator.get_validation_stats()
        }

    def _save_validation_session(self, valid_parlays: List[Dict], invalid_parlays: List[Dict]):
        """Save validation session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for validation in valid_parlays + invalid_parlays:
            parlay = validation["parlay"]
            props_json = json.dumps([
                {
                    "player": leg.prop.player_name,
                    "prop_type": leg.prop.stat_type,
                    "bet_type": leg.prop.bet_type,
                    "line": leg.prop.line
                }
                for leg in parlay.legs
            ])

            parlay_signature = f"{validation['parlay_type']}_{len(parlay.legs)}"

            cursor.execute("""
                INSERT INTO parlay_validation_history
                (parlay_signature, props_json, is_valid, invalid_reason, validated_date, week)
                VALUES (?, ?, ?, ?, datetime('now'), ?)
            """, (
                parlay_signature,
                props_json,
                1 if validation["is_valid"] else 0,
                validation.get("reason"),
                parlay.legs[0].prop.week if parlay.legs else None
            ))

        conn.commit()
        conn.close()

    def quick_validate_parlay(self, parlay: Parlay) -> Tuple[bool, List[str]]:
        """
        Quick validation of a single parlay against rules only (no user input)

        Returns:
            Tuple of (is_valid, violation_reasons)
        """
        return self.validator.validate_parlay_props(parlay.legs)

    def display_validation_stats(self):
        """Display current validation statistics"""
        stats = self.validator.get_validation_stats()

        print("\n" + "="*60)
        print("📊 VALIDATION SYSTEM STATISTICS")
        print("="*60)
        print(f"Total validation rules: {stats['total_rules']}")
        print(f"Props marked available: {stats['props_marked_available']}")
        print(f"Props marked unavailable: {stats['props_marked_unavailable']}")
        print("="*60 + "\n")

    def add_custom_rule_interactive(self):
        """Interactive interface to add custom validation rules"""
        print("\n" + "="*60)
        print("➕ ADD CUSTOM VALIDATION RULE")
        print("="*60)

        print("\nRule Type:")
        print("  1. Same Player Props (e.g., can't combine certain stats)")
        print("  2. Platform Restriction (general unavailability)")

        choice = input("\nSelect rule type (1 or 2): ").strip()

        if choice == '1':
            self._add_same_player_rule()
        elif choice == '2':
            print("Platform restriction rules coming soon!")
        else:
            print("Invalid choice.")

    def _add_same_player_rule(self):
        """Add a same-player combination rule"""
        print("\nExample: Same player can't have UNDER passing yards + UNDER completions")

        description = input("\nRule description: ").strip()

        print("\nProp types (comma-separated, e.g., 'Pass Yds,Completions'): ")
        prop_types = [p.strip() for p in input("  👉 ").split(',')]

        print("\nBet types for each prop (comma-separated, e.g., 'UNDER,UNDER'): ")
        bet_types = [b.strip().upper() for b in input("  👉 ").split(',')]

        if len(prop_types) != len(bet_types):
            print("❌ Number of prop types must match number of bet types")
            return

        conditions = {
            "player": "same",
            "prop_types": prop_types,
            "bet_types": bet_types
        }

        self.validator.add_custom_rule(
            description=description,
            rule_type="same_player_props",
            conditions=conditions,
            auto_applied=True
        )

        print(f"\n✅ Rule added: {description}")
