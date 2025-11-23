"""
Example: How to integrate prop validation into your existing workflow

This shows how to use the validation system with your parlay generation
"""

import sys
import os

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.analysis.data_loader import NFLDataLoader
from scripts.analysis.orchestrator import PropAnalyzer
from scripts.analysis.parlay_builder import ParlayBuilder
from scripts.parlay_validation_cli import validate_and_rebuild_workflow


def example_workflow_with_validation(week: int = 12):
    """
    Complete example: Generate props, build parlays, validate, and rebuild

    This is what you'd run instead of just building parlays directly.
    """
    print("\n" + "="*80)
    print(f"📊 WEEK {week} PARLAY GENERATION WITH VALIDATION")
    print("="*80)

    # Step 1: Load data and analyze props (your existing code)
    print("\n🔍 STEP 1: Loading data and analyzing props...")
    data_loader = NFLDataLoader(data_dir="data")

    try:
        # Use the actual method that exists
        context = data_loader.load_all_data(week=week)
        print(f"   ✅ Loaded data for week {week}")
    except Exception as e:
        print(f"   ❌ Error loading data: {e}")
        return

    # Step 2: Run agent analysis (your existing code)
    print("\n🤖 STEP 2: Running agent analysis...")
    analyzer = PropAnalyzer()

    try:
        # Use the orchestrator's method to analyze all props
        analyzed_props = analyzer.analyze_all_props(context, min_confidence=40)
        print(f"   ✅ Analyzed {len(analyzed_props)} props")
    except Exception as e:
        print(f"   ❌ Error analyzing props: {e}")
        return

    # Step 3: Build initial parlays (your existing code)
    print("\n🎯 STEP 3: Building initial parlays...")
    builder = ParlayBuilder()
    parlays = builder.build_parlays(analyzed_props, min_confidence=58)

    total_parlays = sum(len(p) for p in parlays.values())
    print(f"   ✅ Built {total_parlays} parlays")

    # Step 4: NEW - Validate and rebuild parlays
    print("\n" + "="*80)
    print("🔍 STEP 4: VALIDATION & REBUILD WORKFLOW")
    print("="*80)
    print("\nThis is the NEW step that handles DraftKings Pick6 availability.")

    results = validate_and_rebuild_workflow(
        parlays=parlays,
        all_props=analyzed_props,
        db_path="bets.db"
    )

    # Step 5: Use final parlays (valid + rebuilt)
    final_parlays = results['final_parlays']

    print("\n" + "="*80)
    print("✅ FINAL PARLAYS READY")
    print("="*80)

    # Display final parlays
    formatted = builder.format_parlays_for_betting(final_parlays, "DraftKings Pick6")

    print(formatted)

    # Optionally save to database
    save = input("\n💾 Save these parlays to database? (Y/N): ").strip().upper()
    if save == 'Y':
        from scripts.analysis.parlay_saver import save_parlays_to_db
        save_parlays_to_db(final_parlays, week)
        print("   ✅ Parlays saved!")

    return final_parlays


def quick_validation_check_example():
    """
    Example: Just check existing parlays without rebuilding

    Use this if you already have parlays and just want to validate them
    """
    from scripts.analysis.parlay_validator_interface import ParlayValidatorInterface
    from scripts.analysis.parlay_tracker import ParlayTracker

    print("\n🔍 Quick Validation Check")
    print("="*60)

    # Load existing parlays from database
    tracker = ParlayTracker()
    week = int(input("Which week to validate? "))

    parlays_data = tracker.get_parlays(week=week)

    if not parlays_data:
        print(f"❌ No parlays found for week {week}")
        return

    print(f"✅ Found {len(parlays_data)} parlays")

    # Convert to parlay objects and validate
    # (You'd need to reconstruct Parlay objects from database data)
    # For now, this is a placeholder
    print("\n⚠️  To implement: Reconstruct Parlay objects from database and validate")


def add_custom_rule_example():
    """
    Example: Add a custom validation rule

    Use this to teach the system about new prop combinations that don't work
    """
    from scripts.analysis.parlay_validator_interface import ParlayValidatorInterface

    interface = ParlayValidatorInterface()

    print("\n➕ Adding Custom Validation Rule")
    print("="*60)
    print("\nExample: Same player can't have UNDER touchdowns + UNDER yards")

    interface.validator.add_custom_rule(
        description="Same player: UNDER touchdowns + UNDER yards (any stat type)",
        rule_type="same_player_props",
        conditions={
            "player": "same",
            "prop_types": ["TDs", "Yards"],  # Will match Pass TDs + Pass Yds, etc.
            "bet_types": ["UNDER", "UNDER"]
        },
        auto_applied=True
    )

    print("✅ Custom rule added!")
    interface.display_validation_stats()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validation integration examples")
    parser.add_argument('--mode', choices=['full', 'check', 'add-rule'],
                       default='full',
                       help='Example mode to run')
    parser.add_argument('--week', type=int, default=12,
                       help='Week number')

    args = parser.parse_args()

    if args.mode == 'full':
        example_workflow_with_validation(args.week)
    elif args.mode == 'check':
        quick_validation_check_example()
    elif args.mode == 'add-rule':
        add_custom_rule_example()
