"""
Parlay Validation CLI - Main interface for validating and rebuilding parlays
Integrates with the existing betting system
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict
import argparse
from scripts.analysis.parlay_validator_interface import ParlayValidatorInterface
from scripts.analysis.parlay_rebuilder import ParlayRebuilder
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.analysis.models import PropAnalysis


def main():
    parser = argparse.ArgumentParser(description="Validate and rebuild parlays for DraftKings Pick6")
    parser.add_argument('--mode', choices=['validate', 'rebuild', 'stats', 'add-rule'],
                       default='validate',
                       help='Operation mode')
    parser.add_argument('--db', default='bets.db',
                       help='Database path')

    args = parser.parse_args()

    interface = ParlayValidatorInterface(args.db)
    rebuilder = ParlayRebuilder(args.db)

    if args.mode == 'stats':
        interface.display_validation_stats()

    elif args.mode == 'add-rule':
        interface.add_custom_rule_interactive()

    elif args.mode == 'validate':
        print("\n" + "="*80)
        print("🎯 PARLAY VALIDATION WORKFLOW")
        print("="*80)
        print("\nThis workflow will:")
        print("  1. Load your generated parlays")
        print("  2. Check them against validation rules")
        print("  3. Let you manually validate each one")
        print("  4. Learn which props are available on DraftKings Pick6")
        print("  5. Optionally rebuild parlays using validated props")
        print("\nNote: You'll need to have parlays already generated in the system.")
        print("      Run your parlay generation first, then run this validation.\n")

        # Load parlays from database or JSON
        # For now, we'll provide instructions for integration
        print("⚠️  INTEGRATION REQUIRED:")
        print("   To use this, pass your generated parlays dict to:")
        print("   interface.validate_parlays_interactive(parlays)")
        print("\n   Example integration code:")
        print("""
        from scripts.analysis.parlay_validator_interface import ParlayValidatorInterface

        # After building parlays
        interface = ParlayValidatorInterface()
        results = interface.validate_parlays_interactive(parlays)

        # Rebuild if needed
        if results['invalid_parlays']:
            from scripts.analysis.parlay_rebuilder import ParlayRebuilder
            rebuilder = ParlayRebuilder()

            new_parlays = rebuilder.rebuild_parlays(
                valid_props_pool=results['valid_props_pool'],
                additional_props=all_analyzed_props
            )
        """)

    elif args.mode == 'rebuild':
        print("\n" + "="*80)
        print("🔨 PARLAY REBUILD MODE")
        print("="*80)
        print("\nThis mode rebuilds parlays using validated props.")
        print("Run after validation to get new parlays with only available props.\n")
        print("⚠️  Integration required - see code comments for usage.")


def validate_and_rebuild_workflow(parlays: Dict, all_props: List[PropAnalysis],
                                  db_path: str = "bets.db") -> Dict:
    """
    Complete workflow: Validate existing parlays and rebuild with valid props

    Args:
        parlays: Dict of parlay_type -> List[Parlay] (generated parlays)
        all_props: List of all analyzed props available
        db_path: Database path

    Returns:
        Dict with validation results and rebuilt parlays
    """
    interface = ParlayValidatorInterface(db_path)
    rebuilder = ParlayRebuilder(db_path)

    print("\n" + "="*80)
    print("🎯 COMPLETE VALIDATION & REBUILD WORKFLOW")
    print("="*80)

    # Step 1: Validate existing parlays
    print("\n📋 STEP 1: Validating generated parlays...")
    validation_results = interface.validate_parlays_interactive(parlays)

    valid_parlays = validation_results['valid_parlays']
    invalid_parlays = validation_results['invalid_parlays']
    valid_props_pool = validation_results['valid_props_pool']

    # Step 2: Decide if rebuild is needed
    if not invalid_parlays:
        print("\n✅ All parlays passed validation! No rebuild needed.")
        return {
            "validation_results": validation_results,
            "final_parlays": parlays,
            "rebuild_performed": False
        }

    print(f"\n⚠️  Found {len(invalid_parlays)} invalid parlays")
    print(f"📦 Collected {len(valid_props_pool)} valid props from accepted parlays")

    rebuild = input("\n🔨 Rebuild parlays using validated props? (Y/N): ").strip().upper()

    if rebuild != 'Y':
        print("\n⏭️  Skipping rebuild. Using only valid parlays.")
        return {
            "validation_results": validation_results,
            "final_parlays": {k: [v['parlay'] for v in valid_parlays if v['parlay_type'] == k]
                             for k in parlays.keys()},
            "rebuild_performed": False
        }

    # Step 3: Extract valid props from invalid parlays
    print("\n🔍 Extracting valid props from rejected parlays...")
    extracted_props = rebuilder.extract_valid_props_from_rejected_parlays(invalid_parlays)
    print(f"   ✅ Extracted {len(extracted_props)} valid props")

    # Step 4: Rebuild parlays
    print("\n🔨 Rebuilding parlays...")

    # Calculate how many parlays we need to rebuild
    valid_counts = {}
    for parlay_type in parlays.keys():
        valid_count = len([v for v in valid_parlays if v['parlay_type'] == parlay_type])
        valid_counts[parlay_type] = valid_count

    target_counts = {
        "2-leg": max(0, 3 - valid_counts.get('2-leg', 0)),
        "3-leg": max(0, 3 - valid_counts.get('3-leg', 0)),
        "4-leg": max(0, 3 - valid_counts.get('4-leg', 0)),
        "5-leg": max(0, 1 - valid_counts.get('5-leg', 0))
    }

    print(f"   🎯 Target new parlays: {target_counts}")

    new_parlays = rebuilder.rebuild_parlays(
        valid_props_pool=valid_props_pool + extracted_props,
        additional_props=all_props,
        target_counts=target_counts
    )

    # Step 5: Combine valid + rebuilt parlays
    final_parlays = {}
    for parlay_type in parlays.keys():
        valid_of_type = [v['parlay'] for v in valid_parlays if v['parlay_type'] == parlay_type]
        rebuilt_of_type = new_parlays.get(parlay_type, [])
        final_parlays[parlay_type] = valid_of_type + rebuilt_of_type

    # Summary
    print("\n" + "="*80)
    print("✅ WORKFLOW COMPLETE")
    print("="*80)
    for parlay_type in final_parlays.keys():
        count = len(final_parlays[parlay_type])
        original = len(parlays.get(parlay_type, []))
        print(f"  {parlay_type}: {count} parlays (was {original})")

    return {
        "validation_results": validation_results,
        "final_parlays": final_parlays,
        "rebuild_performed": True,
        "stats": validation_results['stats']
    }


if __name__ == "__main__":
    main()
